-- 00_extensions.sql
-- Run this first in Supabase SQL Editor

-- Enable required extensions (idempotent)
create extension if not exists pgcrypto;

-- No URLs/keys needed for this step.
