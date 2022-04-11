create extension if not exists "uuid-ossp";

create table if not exists schema_version (
    onerow boolean primary key default true,
    version integer not null
);
insert into schema_version (version) values (1) on conflict do nothing;

create table if not exists roles (
    role_id serial primary key,
    role_name text not null,
    can_delete_users boolean not null,
    can_delete_videos boolean not null,
    can_delete_comments boolean not null,
    can_create_roles boolean not null
);
select setval('roles_role_id_seq', 2) where not exists (select * from roles);
insert into roles (
    role_id,
    role_name,
    can_delete_users,
    can_delete_videos,
    can_delete_comments,
    can_create_roles) values
    (1, 'admin', TRUE, TRUE, TRUE, TRUE),
    (2, 'user', FALSE, FALSE, FALSE, FALSE)
    on conflict do nothing;

create table if not exists images (
    image_id uuid primary key default uuid_generate_v4(),
    blob bytea not null,
    content_type text not null
);

create table if not exists users (
    user_id serial primary key,
    role_id int not null default 2,
    handle text unique not null,
    nickname text not null,
    password_hash text not null,
    bio text not null default '',
    avatar_id uuid,
    deleted boolean not null default FALSE,
    foreign key (avatar_id) references images (image_id) on delete set null,
    foreign key (role_id) references roles (role_id) on delete restrict
);
create index if not exists user_handles on users (handle);
select setval('users_user_id_seq', 1) where not exists (select * from users);
insert into users (
    user_id, role_id, handle, nickname,
    password_hash
) values (
    1, 1, 'admin', 'admin',
    '$argon2id$v=19$m=65536,t=3,p=4$dIZFAL1Cwzx/8LuCUi/rOg$wsY3tqxbFrC5eoh/fHNmvtiKmpwxbNqX3Kkjkjn3v18'
) on conflict do nothing;

create table if not exists sessions (
    session_id uuid primary key default uuid_generate_v4(),
    user_id int not null,
    expiration timestamp not null default now() + '2 hours',
    foreign key (user_id) references users (user_id) on delete cascade
);

create table if not exists csrf_tokens (
    csrf_token uuid primary key default uuid_generate_v4(),
    session_id uuid not null,
    expiration timestamp not null default now() + '30 minutes',
    foreign key (session_id) references sessions (session_id) on delete cascade
);

create table if not exists videos (
    video_id uuid primary key default uuid_generate_v4(),
    user_id int not null,
    blob bytea not null,
    content_type text not null,
    title text not null,
    description text not null default '',
    thumbnail_id uuid not null,
    upload_time timestamp not null default now(),
    download_counter int not null default 0,
    video_search_en tsvector generated always as (to_tsvector('english', title || ' ' || description)) stored,
    video_search_fi tsvector generated always as (to_tsvector('finnish', title || ' ' || description)) stored,
    foreign key (user_id) references users (user_id) on delete cascade,
    foreign key (thumbnail_id) references images (image_id) on delete restrict
);
create index if not exists user_videos on videos (user_id);

create table if not exists video_ratings (
    video_id uuid not null,
    user_id int not null,
    rating int not null check (rating = 1 or rating = -1),
    primary key (video_id, user_id),
    foreign key (video_id) references videos (video_id) on delete cascade,
    foreign key (user_id) references users (user_id) on delete cascade
);
create index if not exists specific_video_ratings on video_ratings (video_id);

create table if not exists subscriptions (
    user_id int not null,
    subscribed_id int not null,
    primary key (user_id, subscribed_id),
    foreign key (user_id) references users (user_id) on delete cascade,
    foreign key (subscribed_id) references users (user_id) on delete cascade
);
create index if not exists subbox on subscriptions (user_id);

create table if not exists comments (
    comment_id serial primary key,
    video_id uuid not null,
    user_id int not null,
    timestamp timestamp not null default now(),
    content text not null,
    foreign key (video_id) references videos (video_id) on delete cascade,
    foreign key (user_id) references users (user_id) on delete cascade
);
create index if not exists video_comments on comments (video_id);
