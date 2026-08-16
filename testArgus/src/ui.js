import confetti from 'canvas-confetti';
import { ORBITAL_PLANS, GROUND_STATIONS } from './plans.js';
import { sounds } from './audio.js';

export class UIManager {
  constructor(scene) {
    this.scene = scene;
    this.currentPlan = null;
    this.selectedBilling = 'yearly'; // 'monthly', 'quarterly', 'yearly'
    this.selectedCurrency = 'USD'; // 'USD', 'EUR', 'USDT', 'IRR'
    this.currentLang = 'en'; // 'en', 'fa'
    this.isMuted = false;

    this.initElements();
    this.bindEvents();
    this.startTelemetryLoop();
    this.startLatencySimulator();
  }

  initElements() {
    this.modal = document.getElementById('liquidglass-modal');
    this.modalBackdrop = document.getElementById('modal-backdrop');
    this.hoverTooltip = document.getElementById('hover-tooltip');
    this.telemetryFeed = document.getElementById('telemetry-feed');
    this.soundBtn = document.getElementById('sound-toggle-btn');
    this.langBtn = document.getElementById('lang-toggle-btn');
    this.dockItems = document.querySelectorAll('.orbit-dock-item');
  }

  bindEvents() {
    // Sound toggle
    if (this.soundBtn) {
      this.soundBtn.addEventListener('click', () => {
        sounds.init();
        this.isMuted = sounds.toggleMute();
        this.soundBtn.classList.toggle('muted', this.isMuted);
        const textSpan = this.soundBtn.querySelector('.btn-label');
        if (textSpan) {
          textSpan.textContent = this.isMuted ? (this.currentLang === 'fa' ? 'بی‌صدا' : 'Muted') : (this.currentLang === 'fa' ? 'صوت فضایی' : 'Audio FX');
        }
      });
    }

    // Language toggle
    if (this.langBtn) {
      this.langBtn.addEventListener('click', () => {
        this.currentLang = this.currentLang === 'en' ? 'fa' : 'en';
        document.documentElement.lang = this.currentLang;
        document.documentElement.dir = this.currentLang === 'fa' ? 'rtl' : 'ltr';
        this.langBtn.querySelector('.btn-label').textContent = this.currentLang.toUpperCase();
        this.updateLocalization();
      });
    }

    // Orbit dock items
    this.dockItems.forEach((item) => {
      item.addEventListener('click', () => {
        sounds.init();
        const tier = parseInt(item.dataset.tier);
        this.scene.focusOrbit(tier);
        this.updateActiveDock(tier);
      });
    });

    // Modal close button
    const closeBtn = document.getElementById('modal-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closePlanModal());
    }

    if (this.modalBackdrop) {
      this.modalBackdrop.addEventListener('click', () => this.closePlanModal());
    }

    // Reset camera button
    const resetBtn = document.getElementById('btn-reset-cam');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        sounds.playClick();
        this.scene.resetCamera();
        this.clearActiveDock();
      });
    }

    // Auto-rotate toggle
    const rotateBtn = document.getElementById('btn-toggle-rotate');
    if (rotateBtn) {
      rotateBtn.addEventListener('click', () => {
        sounds.playClick();
        this.scene.isAutoRotate = !this.scene.isAutoRotate;
        rotateBtn.classList.toggle('active', this.scene.isAutoRotate);
      });
    }

    // Direct plan trigger buttons
    document.querySelectorAll('[data-action="open-plan"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        sounds.init();
        const planId = e.currentTarget.dataset.planId;
        const plan = ORBITAL_PLANS.find(p => p.id === planId) || ORBITAL_PLANS[1];
        this.scene.focusOrbit(plan.orbitTier);
        this.openPlanModal(plan);
      });
    });
  }

  updateActiveDock(tier) {
    this.dockItems.forEach(item => {
      if (parseInt(item.dataset.tier) === tier) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  clearActiveDock() {
    this.dockItems.forEach(item => item.classList.remove('active'));
  }

  showHoverTooltip(data) {
    if (!this.hoverTooltip) return;
    if (!data.isHovered) {
      this.hoverTooltip.classList.remove('visible');
      return;
    }

    const { plan, screenX, screenY } = data;
    this.hoverTooltip.innerHTML = `
      <div class="tooltip-header" style="border-left: 3px solid ${plan.color}">
        <span class="tooltip-code">${plan.code}</span>
        <span class="tooltip-altitude">${plan.altitudeKm}</span>
      </div>
      <div class="tooltip-title">${plan.title}</div>
      <div class="tooltip-speed">⚡ ${plan.specs.speed}</div>
      <div class="tooltip-hint">${this.currentLang === 'fa' ? 'برای مشاهده پلن کلیک کنید' : 'Click to inspect orbital plan'}</div>
    `;

    // Position tooltip smoothly near cursor
    const x = Math.min(window.innerWidth - 220, Math.max(20, screenX + 15));
    const y = Math.min(window.innerHeight - 120, Math.max(20, screenY - 20));
    this.hoverTooltip.style.left = `${x}px`;
    this.hoverTooltip.style.top = `${y}px`;
    this.hoverTooltip.classList.add('visible');
  }

  openPlanModal(plan) {
    this.currentPlan = plan;
    this.updateActiveDock(plan.orbitTier);

    if (!this.modal) return;

    this.renderModalContent(plan);
    this.modal.classList.add('active');
    if (this.modalBackdrop) this.modalBackdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  closePlanModal() {
    if (!this.modal) return;
    sounds.playClick();
    this.modal.classList.remove('active');
    if (this.modalBackdrop) this.modalBackdrop.classList.remove('active');
    document.body.style.overflow = '';
  }

  renderModalContent(plan) {
    const isFa = this.currentLang === 'fa';
    const modalBody = document.getElementById('modal-dynamic-content');
    if (!modalBody) return;

    // Calculate prices based on billing selection
    let price = plan.priceYearly;
    let periodText = isFa ? 'سالانه (۴۵٪ تخفیف ویژه)' : 'Yearly (Save 45% + 2 Mo Free)';
    let perMonthPrice = (plan.priceYearly / 12).toFixed(2);

    if (this.selectedBilling === 'monthly') {
      price = plan.priceMonthly;
      periodText = isFa ? 'ماهانه' : 'Monthly';
      perMonthPrice = plan.priceMonthly.toFixed(2);
    } else if (this.selectedBilling === 'quarterly') {
      price = plan.priceQuarterly;
      periodText = isFa ? 'سه ماهه (۲۰٪ تخفیف)' : 'Quarterly (Save 20%)';
      perMonthPrice = (plan.priceQuarterly / 3).toFixed(2);
    }

    let displayCurrency = '$';
    let formattedPrice = price;
    if (this.selectedCurrency === 'EUR') {
      displayCurrency = '€';
      formattedPrice = (price * 0.93).toFixed(2);
    } else if (this.selectedCurrency === 'USDT') {
      displayCurrency = '₮';
      formattedPrice = price.toFixed(2);
    } else if (this.selectedCurrency === 'IRR') {
      displayCurrency = 'تومان ';
      formattedPrice = Math.round(price * plan.irrMultiplier).toLocaleString('fa-IR');
    }

    modalBody.innerHTML = `
      <!-- Modal Liquid Glass Header -->
      <div class="liquid-header" style="background: ${plan.bgGradient}; border-bottom: 1px solid ${plan.color}33;">
        <div class="liquid-header-top">
          <div class="plan-code-badge" style="background: ${plan.color}22; color: ${plan.color}; border: 1px solid ${plan.color}66;">
            <span class="pulse-dot" style="background: ${plan.color};"></span>
            ${plan.code} • ${plan.altitudeKm}
          </div>
          ${plan.isRecommended ? `<span class="recommended-badge">${isFa ? 'پیشنهاد اختصاصی' : 'RECOMMENDED'}</span>` : ''}
        </div>
        <h2 class="plan-title">${isFa ? plan.title : plan.title}</h2>
        <p class="plan-headline">${plan.headline}</p>
      </div>

      <!-- Modal Body Inner -->
      <div class="liquid-body">
        
        <!-- Billing Selector Tabs -->
        <div class="billing-tabs-container">
          <div class="billing-label">${isFa ? 'دوره اشتراک:' : 'Subscription Period:'}</div>
          <div class="billing-tabs">
            <button class="billing-tab ${this.selectedBilling === 'monthly' ? 'active' : ''}" data-billing="monthly">
              ${isFa ? '۱ ماهه' : '1 Month'}
              <span class="tab-sub">${plan.priceMonthly}$/m</span>
            </button>
            <button class="billing-tab ${this.selectedBilling === 'quarterly' ? 'active' : ''}" data-billing="quarterly">
              ${isFa ? '۳ ماهه (-۲۰٪)' : '3 Months (-20%)'}
              <span class="tab-sub">${(plan.priceQuarterly/3).toFixed(2)}$/m</span>
            </button>
            <button class="billing-tab ${this.selectedBilling === 'yearly' ? 'active' : ''}" data-billing="yearly">
              ${isFa ? '۱۲ ماهه (بهترین قیمت)' : '12 Months (Best Value)'}
              <span class="tab-badge">${isFa ? 'ویژه' : 'SAVE 45%'}</span>
            </button>
          </div>
        </div>

        <!-- Pricing Summary Glass Card -->
        <div class="pricing-card" style="border: 1px solid ${plan.color}44;">
          <div class="pricing-main">
            <div class="price-amount">
              <span class="currency-symbol">${displayCurrency}</span>
              <span class="price-val">${formattedPrice}</span>
              <span class="price-period">/ ${periodText}</span>
            </div>
            <div class="price-per-month">
              ${isFa ? `معادل ماهانه: ${perMonthPrice}$` : `Equivalent to only $${perMonthPrice}/mo`}
            </div>
          </div>

          <!-- Currency Switcher -->
          <div class="currency-pills">
            <button class="curr-pill ${this.selectedCurrency === 'USD' ? 'active' : ''}" data-curr="USD">USD ($)</button>
            <button class="curr-pill ${this.selectedCurrency === 'EUR' ? 'active' : ''}" data-curr="EUR">EUR (€)</button>
            <button class="curr-pill ${this.selectedCurrency === 'USDT' ? 'active' : ''}" data-curr="USDT">USDT (₮)</button>
            <button class="curr-pill ${this.selectedCurrency === 'IRR' ? 'active' : ''}" data-curr="IRR">تومان (IRR)</button>
          </div>
        </div>

        <!-- Real-time Live Latency & Speed Matrix -->
        <div class="specs-grid">
          <div class="spec-card">
            <div class="spec-icon">⚡</div>
            <div class="spec-info">
              <div class="spec-title">${isFa ? 'پهنای باند و سرعت' : 'Bandwidth & Uplink'}</div>
              <div class="spec-val">${plan.specs.speed}</div>
            </div>
          </div>
          <div class="spec-card">
            <div class="spec-icon">🛡️</div>
            <div class="spec-info">
              <div class="spec-title">${isFa ? 'عبور از فیلترینگ شدید' : 'Anti-Censorship'}</div>
              <div class="spec-val">${plan.specs.antiDpi}</div>
            </div>
          </div>
          <div class="spec-card">
            <div class="spec-icon">🔒</div>
            <div class="spec-info">
              <div class="spec-title">${isFa ? 'رمزنگاری کوانتومی' : 'Quantum Cryptography'}</div>
              <div class="spec-val">${plan.specs.encryption}</div>
            </div>
          </div>
          <div class="spec-card">
            <div class="spec-icon">📱</div>
            <div class="spec-info">
              <div class="spec-title">${isFa ? 'دستگاه‌های همزمان' : 'Simultaneous Devices'}</div>
              <div class="spec-val">${plan.specs.devices}</div>
            </div>
          </div>
        </div>

        <!-- Protocol Chips -->
        <div class="protocols-section">
          <div class="section-title">${isFa ? 'پروتکل‌های فعال در این مدار:' : 'Active Orbital Protocols:'}</div>
          <div class="protocol-chips">
            ${plan.protocols.map(p => `
              <div class="proto-chip">
                <span class="proto-dot"></span>
                <span class="proto-name">${p.name}</span>
                <span class="proto-status">${p.status}</span>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Feature List -->
        <div class="features-section">
          <div class="section-title">${isFa ? 'امکانات و تضمین‌های سرویس:' : 'Orbital Shield Guarantees:'}</div>
          <ul class="feature-list">
            ${plan.features.map(f => `
              <li>
                <span class="check-icon">✓</span>
                <span>${f}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <!-- Interactive Checkout Trigger -->
        <div class="checkout-action-area">
          <button id="btn-start-checkout" class="btn-liquid-buy" style="background: linear-gradient(135deg, ${plan.color}, #0066ff);">
            <span class="btn-glow-shimmer"></span>
            <span class="btn-text">
              🚀 ${isFa ? 'خرید و فعال‌سازی فوری اشتراک' : 'Provision Instant Orbital Key'}
            </span>
          </button>
          <div class="guarantee-text">
            🛡️ ${isFa ? 'گارانتی ۱۰۰٪ بازگشت وجه تا ۷ روز • فعال‌سازی آنی در ۳ ثانیه' : '100% 7-Day Money-Back Guarantee • Instant 3-Second Provisioning'}
          </div>
        </div>

      </div>
    `;

    // Bind modal sub-events
    modalBody.querySelectorAll('.billing-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        sounds.playClick();
        this.selectedBilling = e.currentTarget.dataset.billing;
        this.renderModalContent(plan);
      });
    });

    modalBody.querySelectorAll('.curr-pill').forEach(pill => {
      pill.addEventListener('click', (e) => {
        sounds.playClick();
        this.selectedCurrency = e.currentTarget.dataset.curr;
        this.renderModalContent(plan);
      });
    });

    const buyBtn = modalBody.querySelector('#btn-start-checkout');
    if (buyBtn) {
      buyBtn.addEventListener('click', () => {
        sounds.playOrbitSelect();
        this.showCheckoutModal(plan);
      });
    }
  }

  showCheckoutModal(plan) {
    const isFa = this.currentLang === 'fa';
    const modalBody = document.getElementById('modal-dynamic-content');
    if (!modalBody) return;

    modalBody.innerHTML = `
      <div class="liquid-header" style="background: ${plan.bgGradient};">
        <div class="plan-code-badge" style="color: ${plan.color};">
          <span class="pulse-dot" style="background: ${plan.color};"></span>
          ${isFa ? 'درگاه امن فعال‌سازی ماهواره‌ای' : 'SECURE ORBITAL PROVISIONING TERMINAL'}
        </div>
        <h2 class="plan-title">${isFa ? 'تأیید و پرداخت نهایی' : 'Complete Your Order'}</h2>
        <p class="plan-headline">${plan.title} (${this.selectedBilling.toUpperCase()})</p>
      </div>

      <div class="liquid-body checkout-form-body">
        
        <!-- Step 1: User Identifier -->
        <div class="form-group">
          <label class="form-label">${isFa ? 'ایمیل یا شناسه تلگرام جهت دریافت لایسنس:' : 'Email or Telegram ID (for subscription recovery):'}</label>
          <input type="text" id="checkout-email" class="glass-input" placeholder="e.g. user@shipien.com or @telegram_user" value="orbital_user_${Math.floor(1000 + Math.random() * 9000)}@shipien.net" />
        </div>

        <!-- Step 2: Payment Method Tabs -->
        <div class="form-group">
          <label class="form-label">${isFa ? 'روش پرداخت را انتخاب کنید:' : 'Select Payment Gateway:'}</label>
          <div class="payment-methods-grid">
            <label class="payment-card active">
              <input type="radio" name="pay-method" value="crypto" checked />
              <div class="pay-title">💎 Crypto (USDT / TON / BTC)</div>
              <div class="pay-desc">${isFa ? 'بدون کارمزد، ناشناس، تایید آنی' : 'Zero fee, Anonymous, Instant'}</div>
            </label>
            <label class="payment-card">
              <input type="radio" name="pay-method" value="card" />
              <div class="pay-title">💳 Credit / Debit Card / Stripe</div>
              <div class="pay-desc">${isFa ? 'ویزا، مسترکارت، اپل‌پی' : 'Visa, Mastercard, Apple Pay'}</div>
            </label>
            <label class="payment-card">
              <input type="radio" name="pay-method" value="zarinpal" />
              <div class="pay-title">🇮🇷 درگاه مستقیم شتاب / تومان</div>
              <div class="pay-desc">${isFa ? 'کارت بانکی ایرانی، تحویل لحظه‌ای' : 'Iranian Bank Cards / Zarinpal'}</div>
            </label>
          </div>
        </div>

        <!-- Step 3: Security & Server Selection -->
        <div class="form-group">
          <label class="form-label">${isFa ? 'موقعیت سرور خروجی اولیه:' : 'Primary Routing Gateway:'}</label>
          <select id="gateway-select" class="glass-select">
            <option value="auto">🌐 Automatic Lowest Latency Smart-Mesh (Recommended)</option>
            <option value="de">🇩🇪 Frankfurt, Germany (Anti-DPI Ultra)</option>
            <option value="ch">🇨🇭 Zurich, Switzerland (Zero-Jurisdiction Privacy)</option>
            <option value="jp">🇯🇵 Tokyo, Japan (10G Gigabit Starlink)</option>
            <option value="sg">🇸🇬 Singapore (Asia Low Latency)</option>
            <option value="us">🇺🇸 New York, USA (Streaming & Netflix)</option>
          </select>
        </div>

        <!-- Checkout Action Button -->
        <div class="checkout-action-area">
          <button id="btn-confirm-payment" class="btn-liquid-buy" style="background: linear-gradient(135deg, ${plan.color}, #00cc88);">
            <span class="btn-text">
              ✨ ${isFa ? 'پرداخت و صدور آنی کانفیگ اختصاصی' : 'Authorize & Generate Orbital Key'}
            </span>
          </button>
          <button id="btn-back-to-plan" class="btn-glass-secondary">
            ← ${isFa ? 'بازگشت به مشخصات پلن' : 'Back to Plan Details'}
          </button>
        </div>

        <!-- Simulated Provisioning Loader -->
        <div id="provision-loader" class="provision-loader" style="display: none;">
          <div class="loader-spinner"></div>
          <div class="loader-status" id="loader-status-text">Allocating dedicated orbital node...</div>
          <div class="loader-terminal" id="loader-terminal-log"></div>
        </div>

      </div>
    `;

    // Handle payment method toggle highlight
    modalBody.querySelectorAll('.payment-card input').forEach(radio => {
      radio.addEventListener('change', () => {
        modalBody.querySelectorAll('.payment-card').forEach(c => c.classList.remove('active'));
        radio.closest('.payment-card').classList.add('active');
        sounds.playClick();
      });
    });

    const backBtn = modalBody.querySelector('#btn-back-to-plan');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        sounds.playClick();
        this.renderModalContent(plan);
      });
    }

    const confirmBtn = modalBody.querySelector('#btn-confirm-payment');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => this.runSimulatedProvisioning(plan));
    }
  }

  runSimulatedProvisioning(plan) {
    const isFa = this.currentLang === 'fa';
    const loader = document.getElementById('provision-loader');
    const statusText = document.getElementById('loader-status-text');
    const terminalLog = document.getElementById('loader-terminal-log');
    const confirmBtn = document.getElementById('btn-confirm-payment');

    if (!loader) return;
    loader.style.display = 'block';
    if (confirmBtn) confirmBtn.style.display = 'none';

    sounds.playOrbitSelect();

    const logs = [
      `[INIT] Handshake request to Orbital Node ${plan.code}...`,
      `[CRYPTO] Generating Post-Quantum Kyber-1024 private key...`,
      `[SECURITY] Binding dynamic multi-hop cipher for user account...`,
      `[ROUTING] Authorizing unthrottled Starlink mesh channel...`,
      `[SUCCESS] Subscription license activated on orbital network!`
    ];

    let step = 0;
    const interval = setInterval(() => {
      if (step < logs.length) {
        if (terminalLog) {
          const line = document.createElement('div');
          line.className = 'terminal-line';
          line.textContent = logs[step];
          terminalLog.appendChild(line);
          terminalLog.scrollTop = terminalLog.scrollHeight;
        }
        if (statusText) {
          statusText.textContent = logs[step];
        }
        sounds.playHover();
        step++;
      } else {
        clearInterval(interval);
        setTimeout(() => {
          this.renderSuccessReceipt(plan);
        }, 500);
      }
    }, 600);
  }

  renderSuccessReceipt(plan) {
    const isFa = this.currentLang === 'fa';
    const modalBody = document.getElementById('modal-dynamic-content');
    if (!modalBody) return;

    sounds.playSuccess();

    // Trigger celebration confetti
    try {
      confetti({
        particleCount: 80,
        spread: 90,
        origin: { y: 0.6 },
        colors: ['#00f0ff', '#a855f7', '#f59e0b', '#10b981', '#ffffff']
      });
    } catch (e) {}

    const randomKey = `vless://usr_${Math.random().toString(36).substring(2, 10)}-${Math.random().toString(36).substring(2, 8)}@${plan.id}.shipien.network:443?encryption=none&security=reality&sni=gateway.orbital.shipien.org&fp=chrome&pbk=7x9K_shipien_kyber_${Math.random().toString(36).substring(2, 8)}&type=grpc&serviceName=orbital-shield#Shipien-${plan.title.replace(/\s+/g, '-')}`;

    modalBody.innerHTML = `
      <div class="liquid-header" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(10, 30, 20, 0.9)); border-bottom: 1px solid #10b98166;">
        <div class="plan-code-badge" style="background: #10b98133; color: #10b981; border: 1px solid #10b981;">
          ✓ ${isFa ? 'اشتراک فعال شد' : 'SUBSCRIPTION ACTIVE'}
        </div>
        <h2 class="plan-title" style="color: #10b981;">🎉 ${isFa ? 'خرید شما با موفقیت انجام شد!' : 'Access Granted! Node Online.'}</h2>
        <p class="plan-headline">${isFa ? 'کانفیگ اختصاصی شما صادر و آماده اتصال است.' : 'Your dedicated orbital cryptographic key has been provisioned.'}</p>
      </div>

      <div class="liquid-body">
        
        <!-- Holographic Pass Card -->
        <div class="holographic-pass-card" style="border: 1px solid ${plan.color}66; box-shadow: 0 0 30px ${plan.color}33;">
          <div class="pass-header">
            <div class="pass-brand">SHIPIEN // ORBITAL KEY</div>
            <div class="pass-orbit">${plan.code} • ${plan.altitudeKm}</div>
          </div>
          
          <div class="pass-content">
            <div class="qr-container">
              <canvas id="receipt-qr-canvas" width="140" height="140"></canvas>
            </div>
            <div class="pass-meta">
              <div class="pass-field">
                <span class="field-label">${isFa ? 'پلن:' : 'Tier:'}</span>
                <span class="field-val" style="color: ${plan.color};">${plan.title}</span>
              </div>
              <div class="pass-field">
                <span class="field-label">${isFa ? 'پروتکل:' : 'Protocol:'}</span>
                <span class="field-val">VLESS Reality + Hysteria2</span>
              </div>
              <div class="pass-field">
                <span class="field-label">${isFa ? 'ترافیک:' : 'Bandwidth:'}</span>
                <span class="field-val">Unlimited Gigabit</span>
              </div>
              <div class="pass-field">
                <span class="field-label">${isFa ? 'وضعیت اتصال:' : 'Status:'}</span>
                <span class="field-val" style="color: #10b981;">● Online & Shielded</span>
              </div>
            </div>
          </div>

          <!-- Key Copy Section -->
          <div class="key-box">
            <input type="text" id="config-uri-input" class="key-input" value="${randomKey}" readonly />
            <button id="btn-copy-config" class="btn-copy-key">
              📋 ${isFa ? 'کپی کانفیگ' : 'Copy Config'}
            </button>
          </div>
        </div>

        <!-- Quick Client App Import Links -->
        <div class="apps-import-section">
          <div class="section-title">${isFa ? 'اتصال سریع با یک کلیک در برنامه‌ها:' : '1-Click Import into Client Apps:'}</div>
          <div class="app-buttons-grid">
            <button class="app-btn" onclick="navigator.clipboard.writeText('${randomKey}'); alert('Config copied! Open Sing-Box and click Import.');">
              <span class="app-icon">📦</span> Sing-Box
            </button>
            <button class="app-btn" onclick="navigator.clipboard.writeText('${randomKey}'); alert('Config copied! Open V2rayNG/V2rayN and paste.');">
              <span class="app-icon">⚡</span> V2rayNG / V2rayN
            </button>
            <button class="app-btn" onclick="navigator.clipboard.writeText('${randomKey}'); alert('Config copied! Open Shadowrocket and import.');">
              <span class="app-icon">🚀</span> Shadowrocket (iOS)
            </button>
            <button class="app-btn" onclick="navigator.clipboard.writeText('${randomKey}'); alert('Config copied! Open Clash Verge and paste.');">
              <span class="app-icon">🛡️</span> Clash Verge / Mihomo
            </button>
          </div>
        </div>

        <!-- Close & Back to Orbit Button -->
        <div class="checkout-action-area" style="margin-top: 24px;">
          <button id="btn-finish-receipt" class="btn-liquid-buy" style="background: linear-gradient(135deg, #10b981, #00f0ff);">
            🌍 ${isFa ? 'مشاهده مدار در وضعیت آنلاین' : 'Return to Orbital Command'}
          </button>
        </div>

      </div>
    `;

    // Draw procedural high-tech QR code matrix
    this.drawProceduralQR('receipt-qr-canvas', plan.color);

    const copyBtn = modalBody.querySelector('#btn-copy-config');
    const inputField = modalBody.querySelector('#config-uri-input');
    if (copyBtn && inputField) {
      copyBtn.addEventListener('click', () => {
        inputField.select();
        navigator.clipboard.writeText(inputField.value);
        sounds.playClick();
        copyBtn.textContent = isFa ? '✓ کپی شد!' : '✓ Copied!';
        setTimeout(() => {
          copyBtn.textContent = isFa ? '📋 کپی کانفیگ' : 'Copy Config';
        }, 2500);
      });
    }

    const finishBtn = modalBody.querySelector('#btn-finish-receipt');
    if (finishBtn) {
      finishBtn.addEventListener('click', () => {
        this.closePlanModal();
      });
    }
  }

  drawProceduralQR(canvasId, accentColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = canvas.width;
    const gridSize = 21;
    const cellSize = size / gridSize;

    ctx.fillStyle = '#061325';
    ctx.fillRect(0, 0, size, size);

    // Draw QR pattern
    ctx.fillStyle = accentColor || '#00f0ff';

    // Position detection squares (Corners)
    const drawCorner = (ox, oy) => {
      ctx.fillRect(ox * cellSize, oy * cellSize, 7 * cellSize, 7 * cellSize);
      ctx.fillStyle = '#061325';
      ctx.fillRect((ox + 1) * cellSize, (oy + 1) * cellSize, 5 * cellSize, 5 * cellSize);
      ctx.fillStyle = accentColor || '#00f0ff';
      ctx.fillRect((ox + 2) * cellSize, (oy + 2) * cellSize, 3 * cellSize, 3 * cellSize);
    };

    drawCorner(0, 0);
    drawCorner(gridSize - 7, 0);
    drawCorner(0, gridSize - 7);

    // Data matrix pseudo-random dots
    for (let r = 0; r < gridSize; r++) {
      for (let c = 0; c < gridSize; c++) {
        // Skip corner markers
        if ((r < 8 && c < 8) || (r < 8 && c >= gridSize - 8) || (r >= gridSize - 8 && c < 8)) {
          continue;
        }
        if (Math.sin(r * 12.3 + c * 45.6) > 0.1) {
          ctx.fillRect(c * cellSize + 1, r * cellSize + 1, cellSize - 2, cellSize - 2);
        }
      }
    }
  }

  startTelemetryLoop() {
    const logs = [
      "LEO-01 • Synced 16 Starlink mesh gateways",
      "MEO-02 • Quantum Kyber-1024 handshake verified",
      "GEO-03 • 100 Gbps dedicated pipeline at 0% loss",
      "POLAR-04 • Subsea fiber failover ready",
      "GLOBAL • 99.998% mesh availability across 12 clusters",
      "SECURITY • Zero logs cryptographically validated"
    ];

    setInterval(() => {
      if (!this.telemetryFeed) return;
      const log = logs[Math.floor(Math.random() * logs.length)];
      const time = new Date().toTimeString().split(' ')[0];
      const item = document.createElement('div');
      item.className = 'telemetry-item';
      item.innerHTML = `<span class="log-time">[${time}]</span> ${log}`;
      this.telemetryFeed.appendChild(item);

      while (this.telemetryFeed.children.length > 5) {
        this.telemetryFeed.removeChild(this.telemetryFeed.firstChild);
      }
    }, 4500);
  }

  startLatencySimulator() {
    setInterval(() => {
      const pingEls = document.querySelectorAll('[data-live-ping]');
      pingEls.forEach(el => {
        const base = parseInt(el.dataset.livePing) || 16;
        const jitter = Math.floor(Math.random() * 5) - 2;
        el.textContent = `${Math.max(8, base + jitter)}ms`;
      });
    }, 2800);
  }

  updateLocalization() {
    const isFa = this.currentLang === 'fa';
    document.querySelectorAll('[data-i18n-en]').forEach(el => {
      el.textContent = isFa ? el.dataset.i18nFa : el.dataset.i18nEn;
    });
    if (this.currentPlan && this.modal && this.modal.classList.contains('active')) {
      this.renderModalContent(this.currentPlan);
    }
  }
}
