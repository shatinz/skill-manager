// Shipien VPN Orbital Plans Specification & Matrix

export const ORBITAL_PLANS = [
  {
    id: "leo-mesh",
    orbitTier: 1,
    orbitName: "LEO Alpha-Mesh",
    altitudeKm: "380 km",
    inclination: "53.2°",
    code: "LEO-01",
    tag: "High Velocity",
    badge: "Ultra Low Latency",
    title: "Orbital Scout",
    headline: "LEO Nano-Mesh Fast Pass",
    description: "Designed for competitive gaming, lightning-fast streaming, and zero-jitter P2P tunneling via low-orbit satellite mesh nodes.",
    color: "#00f0ff", // Electric Cyan
    glowColor: "rgba(0, 240, 255, 0.4)",
    bgGradient: "linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(5, 25, 45, 0.8))",
    priceMonthly: 3.49,
    priceQuarterly: 8.99, // 2.99/mo
    priceYearly: 29.99,   // 2.49/mo
    currencySymbols: { USD: "$", EUR: "€", USDT: "₮", IRR: "تومان" },
    irrMultiplier: 85000,
    specs: {
      speed: "10 Gbps Starlink Uplink",
      latency: "8ms - 18ms",
      devices: "5 Concurrent Devices",
      bandwidth: "Unlimited Unthrottled",
      encryption: "AES-256-GCM / ChaCha20-Poly1305",
      obfuscation: "Dynamic TCP-TLS Mux",
      killSwitch: "Orbital Auto-Sever v2",
      antiDpi: "Level 2 (DPI Shield)"
    },
    protocols: [
      { name: "WireGuard Turbo", status: "Optimal" },
      { name: "VLESS-Reality", status: "Enabled" },
      { name: "Shadowsocks 2022", status: "Active" }
    ],
    features: [
      "Ultra-low latency LEO satellite mesh routing",
      "Dynamic IP rotation every 15 minutes or on-demand",
      "Optimized for 4K/8K HDR streaming & Discord/Gaming",
      "Zero logs cryptographically signed policy",
      "Instant 1-Click QR Setup on iOS, Android, Windows, Mac, Linux"
    ],
    satelliteCount: 16,
    activeGateways: ["Frankfurt", "Tokyo", "Singapore", "New York"]
  },
  {
    id: "meo-shield",
    orbitTier: 2,
    orbitName: "MEO Argus Shield",
    altitudeKm: "2,020 km",
    inclination: "64.8°",
    code: "MEO-02",
    tag: "Most Popular",
    badge: "Argus Stealth Matrix",
    title: "Argus Aegis Pro",
    headline: "Military-Grade Quantum Stealth Shield",
    description: "Equipped with proprietary Argus Deep-Packet-Inspection bypass technology, dual-hop satellite relays, and quantum-resistant key exchanges.",
    color: "#a855f7", // Holographic Violet / Electric Purple
    glowColor: "rgba(168, 85, 247, 0.4)",
    bgGradient: "linear-gradient(135deg, rgba(168, 85, 247, 0.18), rgba(20, 10, 40, 0.8))",
    isRecommended: true,
    priceMonthly: 6.99,
    priceQuarterly: 17.99, // 5.99/mo
    priceYearly: 59.99,    // 4.99/mo
    currencySymbols: { USD: "$", EUR: "€", USDT: "₮", IRR: "تومان" },
    irrMultiplier: 85000,
    specs: {
      speed: "25 Gbps High-Throughput",
      latency: "18ms - 32ms",
      devices: "10 Concurrent Devices",
      bandwidth: "Unlimited Unmetered",
      encryption: "Post-Quantum Kyber-1024 + ChaCha20",
      obfuscation: "Argus Deep-Chameleon DPI Killer",
      killSwitch: "Hardware Layer Kernel Killswitch",
      antiDpi: "Level 5 (Maximum Bypass - Iran/China Tested)"
    },
    protocols: [
      { name: "VLESS + XTLS Vision Reality", status: "Optimal" },
      { name: "Hysteria 2 (UDP Turbo)", status: "Optimal" },
      { name: "TUIC v5 (BBR Congestion)", status: "Optimal" },
      { name: "Shadowsocks 2022 BLAKE3", status: "Active" },
      { name: "Trojan-gRPC", status: "Active" }
    ],
    features: [
      "Argus Quantum-Resistant Handshake (Kyber-1024)",
      "Deep Packet Inspection (DPI) undetectable camouflage",
      "Hysteria 2 protocol with 99.8% packet loss survival",
      "Multi-Hop Cascade (Route via Switzerland -> Tokyo -> US)",
      "Residential & Datacenter clean IP pool (Never blacklisted)",
      "Dedicated 24/7 VIP Orbital Ops Support"
    ],
    satelliteCount: 12,
    activeGateways: ["Zurich", "Frankfurt", "Tokyo", "Singapore", "London", "Tehran-Bypass"]
  },
  {
    id: "geo-titan",
    orbitTier: 3,
    orbitName: "GEO Sovereign Titan",
    altitudeKm: "35,786 km",
    inclination: "0.0° (Equatorial)",
    code: "GEO-03",
    tag: "Enterprise Tier",
    badge: "Dedicated Orbital Circuit",
    title: "Cosmic Sovereign",
    headline: "Uncapped Dedicated Orbital Pipeline",
    description: "Geostationary dedicated private satellite circuit with static residential clean IPs, isolated bandwidth trunk, and sovereign multi-tenant isolation.",
    color: "#f59e0b", // Radiant Amber Gold
    glowColor: "rgba(245, 158, 11, 0.4)",
    bgGradient: "linear-gradient(135deg, rgba(245, 158, 11, 0.16), rgba(35, 20, 5, 0.8))",
    priceMonthly: 12.99,
    priceQuarterly: 32.99, // 10.99/mo
    priceYearly: 109.99,   // 9.16/mo
    currencySymbols: { USD: "$", EUR: "€", USDT: "₮", IRR: "تومان" },
    irrMultiplier: 85000,
    specs: {
      speed: "100 Gbps Dedicated Line",
      latency: "28ms - 45ms",
      devices: "Unlimited Devices (Family & Team)",
      bandwidth: "Sovereign Unmetered Dedicated",
      encryption: "Triple-Layer AES-256-GCM + XChaCha20",
      obfuscation: "Custom Port & SNI Mimicry",
      killSwitch: "BGP Autonomous Auto-Reroute",
      antiDpi: "Level 5+ (Dedicated Clean Fiber Subsea Link)"
    },
    protocols: [
      { name: "Dedicated VLESS Private Node", status: "Exclusive" },
      { name: "Shadowsocks 2022 Multi-User", status: "Active" },
      { name: "WireGuard Kernel Mode", status: "Optimal" },
      { name: "Hysteria 2 BBR3", status: "Optimal" }
    ],
    features: [
      "1x Dedicated Static Clean Residential IP (US, DE, UK, JP or CH)",
      "Uncapped multi-gigabit throughput with 0% throttling",
      "Unlimited simultaneous connections for entire teams or households",
      "Custom DNS filtering, Ad-Shield, and Malware interceptor",
      "Sing-box, Clash Meta, and Shadowrocket auto-updating profiles",
      "Direct Priority Satellite link channel"
    ],
    satelliteCount: 8,
    activeGateways: ["Zurich", "New York", "Tokyo", "London", "Dubai", "Singapore", "Frankfurt"]
  },
  {
    id: "polar-aurora",
    orbitTier: 4,
    orbitName: "Polar Deep Orbit",
    altitudeKm: "1,200 km (Polar)",
    inclination: "98.7° (Sun-Synchronous)",
    code: "POLAR-04",
    tag: "Extreme Bypass",
    badge: "Sub-Zero Infiltration",
    title: "Cipher Aurora",
    headline: "Zero-Knowledge Planetary Infiltration",
    description: "Rotates longitudinally over polar axes to bypass all terrestrial jurisdictional borders and national firewalls through sub-orbital laser meshes.",
    color: "#10b981", // Emerald Aurora
    glowColor: "rgba(16, 185, 129, 0.4)",
    bgGradient: "linear-gradient(135deg, rgba(16, 185, 129, 0.16), rgba(5, 30, 20, 0.8))",
    priceMonthly: 8.99,
    priceQuarterly: 22.99, // 7.66/mo
    priceYearly: 79.99,    // 6.66/mo
    currencySymbols: { USD: "$", EUR: "€", USDT: "₮", IRR: "تومان" },
    irrMultiplier: 85000,
    specs: {
      speed: "40 Gbps Polar Laser Link",
      latency: "20ms - 38ms",
      devices: "15 Concurrent Devices",
      bandwidth: "Unlimited High Priority",
      encryption: "Double Ratchet + Noise Protocol Framework",
      obfuscation: "Morphing Traffic Signature v3",
      killSwitch: "Instant Memory RAM Wipe",
      antiDpi: "Level 5 (Total Stealth)"
    },
    protocols: [
      { name: "VLESS Reality + gRPC", status: "Optimal" },
      { name: "TUIC v5 Native", status: "Optimal" },
      { name: "Hysteria 2 Protocol", status: "Optimal" },
      { name: "Shadowsocks 2022", status: "Active" }
    ],
    features: [
      "Polar cross-link laser communication mesh",
      "Guaranteed operation during total internet blackouts",
      "Automatic failover between 120+ planetary nodes",
      "No email or personal information required (RAM-only authentication)",
      "Compatible with all routers, consoles, mobile, and desktops"
    ],
    satelliteCount: 12,
    activeGateways: ["Reykjavik", "Stockholm", "Helsinki", "Zurich", "Tokyo", "Vancouver"]
  }
];

export const GROUND_STATIONS = [
  { name: "Frankfurt Hub", lon: 8.68, lat: 50.1, code: "FRA-01", ping: 12, region: "Europe" },
  { name: "Tokyo Core", lon: 139.7, lat: 35.6, code: "TYO-02", ping: 18, region: "Asia Pacific" },
  { name: "Singapore Gateway", lon: 103.8, lat: 1.35, code: "SIN-03", ping: 22, region: "SE Asia" },
  { name: "New York Terminal", lon: -74.0, lat: 40.7, code: "NYC-04", ping: 15, region: "North America" },
  { name: "Zurich Vault", lon: 8.54, lat: 47.3, code: "ZRH-05", ping: 14, region: "Europe Privacy" },
  { name: "London Relay", lon: -0.12, lat: 51.5, code: "LDN-06", ping: 16, region: "UK Hub" },
  { name: "Dubai Orbital", lon: 55.3, lat: 25.2, code: "DXB-07", ping: 24, region: "Middle East" },
  { name: "Tehran Stealth", lon: 51.4, lat: 35.7, code: "THR-08", ping: 29, region: "Argus Bypass" },
  { name: "São Paulo Node", lon: -46.6, lat: -23.5, code: "SAO-09", ping: 35, region: "South America" },
  { name: "Sydney Link", lon: 151.2, lat: -33.8, code: "SYD-10", ping: 38, region: "Oceania" }
];
