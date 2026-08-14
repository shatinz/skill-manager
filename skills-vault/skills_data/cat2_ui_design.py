"""
Category 2: UI Design & Anti-Slop (6 Skills)
"""

UI_DESIGN_SKILLS = [
    {
        "id": "ui-design-antislop.styling-tokens.tailwind-v4-tokens",
        "name": "tailwind-v4-tokens",
        "title": "Tailwind CSS v4 CSS-First Design Tokens & Theme Craft",
        "category": "ui-design-antislop",
        "subcategory": "styling-tokens",
        "version": "1.1.0",
        "tags": ["tailwind-v4", "css-variables", "design-tokens", "theme", "oklch", "container-queries"],
        "trust_rating": 0.98,
        "estimated_tokens": 1550,
        "description": "Configure and structure CSS-first theme tokens in Tailwind CSS v4 using @theme directives, OKLCH wide-gamut palettes, dynamic dark mode variables, and container queries without javascript config files.",
        "trigger_patterns": [
            "tailwind v4 theme tokens",
            "tailwind v4 css @theme directive",
            "tailwind v4 oklch colors",
            "tailwind 4 container queries",
            "migrate to tailwind v4"
        ],
        "content": """# Tailwind CSS v4 CSS-First Design Tokens & Theme Craft

## Objective
Adopt Tailwind CSS v4's CSS-first architecture using `@theme` blocks, `@utility` definitions, and OKLCH color spaces to build responsive, tokenized design systems with zero JS configuration.

## Key Principles
1. **Zero-JS Config**: `tailwind.config.js` is replaced with standard `@theme` in CSS.
2. **OKLCH Color Space**: Provides perceptually uniform lightness across hues for predictable dark/light mode balance.
3. **Container Query First**: Use `@container` and `@sm`, `@md` container variants for component-driven layout flexibility.

## Production CSS Token Structure (`src/styles/app.css`)
```css
@import "tailwindcss";

@theme {
  --font-sans: 'Inter Variable', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* OKLCH Wide-Gamut Palette */
  --color-brand-50: oklch(0.97 0.02 260);
  --color-brand-500: oklch(0.62 0.22 260);
  --color-brand-600: oklch(0.52 0.24 260);
  --color-brand-900: oklch(0.24 0.12 260);

  --color-surface-base: oklch(0.99 0 0);
  --color-surface-subtle: oklch(0.95 0.01 260);
  --color-surface-elevated: oklch(1.0 0 0);
  --color-border-subtle: oklch(0.90 0.01 260);
  --color-text-primary: oklch(0.18 0.02 260);
  --color-text-secondary: oklch(0.45 0.03 260);

  --radius-subtle: 0.375rem;
  --radius-panel: 0.75rem;
}

@media (prefers-color-scheme: dark) {
  @theme {
    --color-surface-base: oklch(0.14 0.02 260);
    --color-surface-subtle: oklch(0.18 0.03 260);
    --color-surface-elevated: oklch(0.22 0.03 260);
    --color-border-subtle: oklch(0.28 0.03 260);
    --color-text-primary: oklch(0.96 0.01 260);
    --color-text-secondary: oklch(0.72 0.02 260);
  }
}

@utility glass-panel {
  background-color: oklch(from var(--color-surface-elevated) l c h / 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-panel);
}
```

## Anti-Patterns
- ❌ Hardcoding arbitrary hex codes (`#1a202c`) inside classes instead of utilizing semantic theme tokens.
- ❌ Retaining legacy JavaScript config files (`tailwind.config.js`) in fresh Tailwind v4 projects.
"""
    },

    {
        "id": "ui-design-antislop.component-systems.shadcn-ui-mastery",
        "name": "shadcn-ui-mastery",
        "title": "shadcn/ui Component Composition & Radix Primitives",
        "category": "ui-design-antislop",
        "subcategory": "component-systems",
        "version": "1.3.0",
        "tags": ["shadcn-ui", "radix-ui", "cva", "tailwind", "accessibility", "react"],
        "trust_rating": 0.99,
        "estimated_tokens": 1600,
        "description": "Compose accessible, customizable design systems using shadcn/ui patterns, Radix UI unstyled primitives, Class Variance Authority (CVA), and the cn() tailwind-merge helper.",
        "trigger_patterns": [
            "shadcn ui component composition",
            "radix ui accessibility shadcn",
            "class variance authority cva button",
            "cn tailwind merge clsx helper"
        ],
        "content": """# shadcn/ui Component Composition & Radix Primitives

## Objective
Build fully accessible (WAI-ARIA compliant), theme-ready component architectures using shadcn/ui composition principles with CVA variants and polymorphic `asChild` Radix slots.

## Production Blueprint (`components/ui/button.tsx`)
```tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
        outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-10 rounded-md px-8',
        icon: 'h-9 w-9',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
```

## Anti-Patterns
- ❌ Overriding styles with `!important` instead of passing clean class overrides merged via `cn()`.
- ❌ Breaking keyboard accessibility by replacing Radix Dialog/Dropdown with manual click-toggle state divs.
"""
    },

    {
        "id": "ui-design-antislop.animations.framer-motion-orchestrator",
        "name": "framer-motion-orchestrator",
        "title": "Framer Motion Physics-Based Orchestration & Layout Transitions",
        "category": "ui-design-antislop",
        "subcategory": "animations",
        "version": "1.2.0",
        "tags": ["framer-motion", "motion", "spring-physics", "layout-animations", "animid-presence", "react"],
        "trust_rating": 0.96,
        "estimated_tokens": 1500,
        "description": "Orchestrate natural, spring-physics UI animations, shared layout transitions with layoutId, staggered container entrances, and exit transitions using Framer Motion.",
        "trigger_patterns": [
            "framer motion spring animation",
            "framer motion layoutId transition",
            "framer motion staggered children",
            "animate presence exit animation"
        ],
        "content": """# Framer Motion Physics-Based Orchestration

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
"""
    },

    {
        "id": "ui-design-antislop.3d-graphics.threejs-procedural-canvas",
        "name": "threejs-procedural-canvas",
        "title": "Three.js & React Three Fiber Procedural 3D Canvas",
        "category": "ui-design-antislop",
        "subcategory": "3d-graphics",
        "version": "1.1.0",
        "tags": ["threejs", "r3f", "webgl", "shaders", "glsl", "procedural", "canvas"],
        "trust_rating": 0.93,
        "estimated_tokens": 1600,
        "description": "Construct high-performance interactive 3D procedural scenes, custom GLSL shaders, post-processing bloom, and responsive canvas viewports using Three.js and React Three Fiber.",
        "trigger_patterns": [
            "react three fiber canvas setup",
            "threejs procedural geometry glsl",
            "r3f custom shader material",
            "threejs webgl performance dispose"
        ],
        "content": """# Three.js & React Three Fiber Procedural 3D Canvas

## Objective
Render smooth 60fps procedural WebGL canvases, custom GLSL vertex/fragment shaders, and memory-safe scene graphs with proper geometry/material disposal.

## Blueprint (`components/ProceduralOrb.tsx`)
```tsx
import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const vertexShader = `
  varying vec2 vUv;
  varying vec3 vNormal;
  uniform float uTime;

  void main() {
    vUv = uv;
    vNormal = normal;
    vec3 pos = position;
    pos += normal * sin(pos.y * 4.0 + uTime * 2.0) * 0.08;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

const fragmentShader = `
  varying vec2 vUv;
  varying vec3 vNormal;
  uniform float uTime;

  void main() {
    vec3 color = 0.5 + 0.5 * cos(uTime + vUv.xyx + vec3(0, 2, 4));
    gl_FragColor = vec4(color, 0.9);
  }
`;

function AnimatedMesh() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
    }),
    []
  );

  useFrame((_, delta) => {
    uniforms.uTime.value += delta;
    meshRef.current.rotation.y += delta * 0.2;
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1.5, 32]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
      />
    </mesh>
  );
}

export function ProceduralCanvas() {
  return (
    <div className="w-full h-96 rounded-2xl overflow-hidden bg-black">
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <AnimatedMesh />
      </Canvas>
    </div>
  );
}
```

## Anti-Patterns
- ❌ Creating geometries or textures inside `useFrame` render loops (causes rapid VRAM leaks).
- ❌ Forgetting `geometry.dispose()` and `material.dispose()` on component unmounts.
"""
    },

    {
        "id": "ui-design-antislop.visual-design.glassmorphic-dark-ui",
        "name": "glassmorphic-dark-ui",
        "title": "Bespoke Glassmorphism, Micro-Gradients & Anti-Slop Visuals",
        "category": "ui-design-antislop",
        "subcategory": "visual-design",
        "version": "1.2.0",
        "tags": ["glassmorphism", "dark-mode", "visual-design", "backdrop-filter", "mesh-gradient", "css"],
        "trust_rating": 0.97,
        "estimated_tokens": 1500,
        "description": "Design high-craft visual interfaces that eliminate generic AI slop: multi-stop mesh gradients, specular highlight borders, optical backdrop blur, micro-interactions, and pristine contrast hierarchies.",
        "trigger_patterns": [
            "bespoke dark mode ui design",
            "anti slop modern ui styling",
            "glassmorphic specular border card",
            "mesh gradient background css"
        ],
        "content": """# Bespoke Glassmorphism, Micro-Gradients & Anti-Slop Visuals

## Objective
Eradicate bland, formulaic AI UI designs (dull flat grays, excessive generic glows, unreadable low-contrast text). Craft bespoke visual interfaces with layered optical depth, delicate multi-point specular borders, subtle SVG grain noise, and intentional typography.

## Anti-Slop Visual Manifesto
1. **No Monotone Gray Deserts**: Base surfaces on deeply tinted zinc, indigo, or obsidian palettes (`oklch(0.14 0.02 260)`), not flat `#111111`.
2. **Specular Light Gradients**: Apply 1px border gradients with a top-down light source simulation (light top edge, subtle dark bottom edge).
3. **Restrained Depth**: Reserve backdrop blurs (`backdrop-blur-md`) for overlays and sticky navigation, combined with `bg-opacity` between 60-80% to preserve legibility.

## Production CSS Blueprint (`styles/glass-craft.css`)
```css
/* Multi-layer Specular Card */
.craft-card {
  position: relative;
  background: radial-gradient(120% 120% at 50% 0%, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%),
              rgba(15, 17, 23, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5),
              inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
}

/* Subtle Animated Ambient Gradient Glow */
.ambient-glow {
  position: absolute;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 300px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.05) 50%, transparent 70%);
  filter: blur(50px);
  pointer-events: none;
  z-index: 0;
}
```

## Anti-Patterns
- ❌ Low-contrast gray text on dark blur backgrounds that violates WCAG AA 4.5:1 ratio.
- ❌ Overusing heavy unconstrained box-shadows that cause repaint lags on low-end GPUs.
"""
    },

    {
        "id": "ui-design-antislop.responsive-layout.responsive-mobile-first-layout",
        "name": "responsive-mobile-first-layout",
        "title": "Responsive Mobile-First Fluid Grid & Adaptive Layouts",
        "category": "ui-design-antislop",
        "subcategory": "responsive-layout",
        "version": "1.2.0",
        "tags": ["responsive-design", "mobile-first", "css-grid", "clamp", "viewport", "touch-targets"],
        "trust_rating": 0.98,
        "estimated_tokens": 1450,
        "description": "Construct adaptive, mobile-first responsive layouts using CSS clamp() fluid typography, CSS Grid auto-fit patterns, 44px touch-target compliance, and iOS safe-area insets.",
        "trigger_patterns": [
            "mobile first responsive layout",
            "css clamp fluid typography",
            "css grid auto-fit responsive minmax",
            "safe-area-inset mobile web layout"
        ],
        "content": """# Responsive Mobile-First Fluid Grid & Adaptive Layouts

## Objective
Build flawless cross-device interfaces that fluidly scale from 320px mobile screens to 4K ultra-wide monitors without jarring breakpoint snaps or horizontal overflow.

## Best Practices
1. **Fluid Sizing with `clamp()`**: Define font sizes and padding that smoothly interpolate based on viewport width: `font-size: clamp(1.125rem, 1rem + 0.8vw, 1.75rem);`.
2. **Auto-Fitting Grids**: Avoid rigid column numbers. Use `grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));`.
3. **Touch Targets & Safe Areas**: Ensure interactive elements meet the minimum 44x44px target size and respect `padding-bottom: env(safe-area-inset-bottom)`.

## Production Tailwind Layout Blueprint
```tsx
export function AdaptiveDashboardGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          {children}
        </div>
      </main>
    </div>
  );
}
```

## Anti-Patterns
- ❌ Desktop-first media queries (`@media (max-width: ...)`) that overload mobile devices with unnecessary overrides.
- ❌ Fixed-width containers (`width: 1200px`) that cause horizontal scrollbars on mobile viewports.
"""
    },

    {
        "id": "ui-design-antislop.component-design.shadcn-tailwind-accessible-ui",
        "name": "shadcn-tailwind-accessible-ui",
        "title": "Shadcn UI & Tailwind CSS Accessible Component Craft",
        "category": "ui-design-antislop",
        "subcategory": "component-design",
        "version": "1.3.0",
        "tags": ["shadcn", "radix-ui", "tailwind-css", "cva", "accessibility", "wcag", "aria"],
        "trust_rating": 0.99,
        "estimated_tokens": 1850,
        "description": "Construct accessible, themeable design systems using Radix UI primitives, Class Variance Authority (CVA), Tailwind CSS v4 variables, and keyboard navigation.",
        "trigger_patterns": [
            "shadcn ui component design",
            "class variance authority cva button",
            "radix ui dialog accessible modal",
            "tailwind css design system tokens"
        ],
        "content": """# Shadcn UI & Tailwind CSS Accessible Component Craft

## Objective
Author battle-tested, accessible React component primitives with Radix UI headless logic, variant styling via `class-variance-authority` (CVA), and dark/light color tokens.

## Button Component (`src/components/ui/button.tsx`)
```tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
```

## Anti-Patterns
- ❌ Hardcoding arbitrary hex values (`bg-[#6366f1]`) instead of CSS semantic design tokens (`bg-primary`, `bg-muted`).
- ❌ Dropping `focus-visible:ring` outlines, breaking keyboard accessibility for disabled users.
"""
    }
]

