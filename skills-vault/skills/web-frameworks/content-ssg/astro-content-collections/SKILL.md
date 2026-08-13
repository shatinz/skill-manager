---
id: web-frameworks.content-ssg.astro-content-collections
name: astro-content-collections
title: Astro Content Collections & Islands Architecture
category: web-frameworks
subcategory: content-ssg
version: 1.3.0
tags:
- astro
- content-collections
- islands
- zod
- ssg
- mdx
- performance
trust_rating: 0.97
estimated_tokens: 1450
description: Construct blazing-fast content-driven static and hybrid websites with
  Astro 5 Content Collections, strict Zod schema validation, and selective island
  hydration.
trigger_patterns:
- astro content collections zod
- astro islands architecture hydration
- astro mdx blog static site
- astro client:load client:visible
---

# Astro Content Collections & Islands Architecture

## Objective
Build zero-JavaScript-by-default websites using Astro 5 Content Layer, Markdown/MDX type-safety, and selective client component hydration (`client:load`, `client:visible`).

## Content Layer Schema (`src/content.config.ts`)
```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/data/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string().max(80),
      description: z.string(),
      pubDate: z.coerce.date(),
      coverImage: image().optional(),
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
    }),
});

export const collections = { blog };
```

## Dynamic Static Page (`src/pages/blog/[slug].astro`)
```astro
---
import { getCollection, render } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import InteractiveComments from '../../components/InteractiveComments.tsx';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await render(post);
---

<BaseLayout title={post.data.title}>
  <article class="prose max-w-3xl mx-auto py-12">
    <h1>{post.data.title}</h1>
    <time>{post.data.pubDate.toLocaleDateString()}</time>
    <Content />
    
    <!-- Island hydrated only when scrolled into view -->
    <InteractiveComments client:visible postId={post.id} />
  </article>
</BaseLayout>
```

## Anti-Patterns
- ❌ Hydrating entire page headers/footers with `client:load` when pure static HTML suffices.
- ❌ Bypassing Content Collections with raw filesystem reads.
