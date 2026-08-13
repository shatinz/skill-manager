# Supabase Postgres Row-Level Security (RLS) & Realtime Channels

## Objective
Enforce database-level multi-tenant security using PostgreSQL RLS policies with `auth.uid()`, coupled with real-time broadcast and presence subscriptions via the Supabase client.

## Bulletproof Multi-Tenant RLS Blueprint
```sql
-- Enable RLS on core tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 1. Helper function to check organization membership without recursive policy queries
CREATE OR REPLACE FUNCTION is_org_member(_org_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_id = _org_id
      AND user_id = auth.uid()
  );
$$;

-- 2. Documents Policy: Read access for organization members
CREATE POLICY "Users can read documents belonging to their organizations"
ON documents
FOR SELECT
TO authenticated
USING (
  is_org_member(org_id)
);

-- 3. Documents Policy: Insert access with ownership assignment
CREATE POLICY "Users can create documents in their organizations"
ON documents
FOR INSERT
TO authenticated
WITH CHECK (
  is_org_member(org_id) AND
  created_by = auth.uid()
);
```

## TypeScript Realtime Channel Integration
```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);

export function subscribeToDocumentChanges(orgId: string, onUpdate: (payload: any) => void) {
  const channel = supabase
    .channel(`org-docs:${orgId}`)
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'documents',
        filter: `org_id=eq.${orgId}`,
      },
      (payload) => {
        onUpdate(payload);
      }
    )
    .subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        console.log('Realtime document channel active');
      }
    });

  return () => {
    supabase.removeChannel(channel);
  };
}
```

## Anti-Patterns
- ❌ Relying on client-side WHERE clauses for security instead of declarative RLS policies.
- ❌ Calling un-indexed subqueries inside RLS `USING` expressions (kills query throughput at scale).