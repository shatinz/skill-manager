---
id: ui-design-antislop.animations.framer-motion-orchestrator
name: framer-motion-orchestrator
title: Framer Motion Physics-Based Orchestration & Layout Transitions
category: ui-design-antislop
subcategory: animations
version: 1.2.0
tags:
- framer-motion
- motion
- spring-physics
- layout-animations
- animid-presence
- react
trust_rating: 0.96
estimated_tokens: 1500
description: Orchestrate natural, spring-physics UI animations, shared layout transitions
  with layoutId, staggered container entrances, and exit transitions using Framer
  Motion.
trigger_patterns:
- framer motion spring animation
- framer motion layoutId transition
- framer motion staggered children
- animate presence exit animation
---

# Framer Motion Physics-Based Orchestration

## Objective
Implement physics-driven, organic animations with zero layout jitter, fluid shared element transitions, and staggered component entrances.

## Blueprint (`components/AnimatedTaskFeed.tsx`)
```tsx
import { motion, AnimatePresence } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 15, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 350, damping: 25 },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.15 },
  },
};

export function AnimatedTaskFeed({ tasks, onRemove }: { tasks: any[]; onRemove: (id: string) => void }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-3"
    >
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <motion.li
            key={task.id}
            layout
            variants={itemVariants}
            exit="exit"
            className="p-4 bg-white dark:bg-zinc-800 rounded-lg shadow-sm flex justify-between items-center"
          >
            <span>{task.title}</span>
            <button
              onClick={() => onRemove(task.id)}
              className="text-red-500 hover:text-red-700 text-sm font-medium"
            >
              Dismiss
            </button>
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  );
}
```

## Anti-Patterns
- ❌ Animating `height` or `width` from 0 to auto without `layout` or CSS grid tricks.
- ❌ Using linear or arbitrary bezier curves for UI micro-interactions; prefer damped spring physics (`type: 'spring'`).
