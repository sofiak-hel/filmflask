update schema_version set version = 2;

alter table users alter column avatar_id drop not null; 