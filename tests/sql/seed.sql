INSERT INTO public.organizations (id, name, created, last_modified)
VALUES ('31537169-4c5d-45db-9d2f-1789fb97692f','New Organization Name', NOW(), NOW());

INSERT INTO public.users(id, name, email, role, organization_id, password_hash, created, last_modified)
VALUES('6ecd25e3-bd58-4f3c-bbe0-a55eb07141f3','dummy','dummy@me.com','APPROVER','31537169-4c5d-45db-9d2f-1789fb97692f','$argon2id$v=19$m=16,t=2,p=1$b1YwbkhuQXl1RUVWWFU1eA$kTk6dXmY6U5CbgBl/dSjXw', NOW(), NOW())