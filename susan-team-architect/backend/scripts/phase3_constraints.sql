-- Phase 3 Wave 1: Expand check constraints for new data types
-- Run in Supabase SQL Editor or via: supabase db execute < scripts/phase3_constraints.sql

-- 1. Allow new episodic memory types (email, calendar_event, reminder, meeting)
ALTER TABLE jake_episodic DROP CONSTRAINT IF EXISTS jake_episodic_memory_type_check;
ALTER TABLE jake_episodic ADD CONSTRAINT jake_episodic_memory_type_check
CHECK (memory_type IN ('conversation', 'email', 'calendar_event', 'task_completed', 'action', 'reminder', 'meeting'));

-- 2. Allow new semantic categories (task_summary, schedule)
ALTER TABLE jake_semantic DROP CONSTRAINT IF EXISTS jake_semantic_category_check;
ALTER TABLE jake_semantic ADD CONSTRAINT jake_semantic_category_check
CHECK (category IN ('fact', 'preference', 'decision', 'task', 'task_summary', 'pattern', 'procedure', 'schedule'));

-- 3. Allow new entity types (colleague, recurring_event, location)
ALTER TABLE jake_entities DROP CONSTRAINT IF EXISTS jake_entities_entity_type_check;
ALTER TABLE jake_entities ADD CONSTRAINT jake_entities_entity_type_check
CHECK (entity_type IN ('person', 'family_member', 'company', 'project', 'colleague', 'recurring_event', 'technology', 'team', 'location'));
