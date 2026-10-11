// AutoFlow Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Close mobile menu when clicking links
    document.querySelectorAll('#mobile-menu a').forEach(link => {
        link.addEventListener('click', () => mobileMenu.classList.add('hidden'));
    });
    
    // FAQ Accordion
    document.querySelectorAll('.faq-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const faqItem = this.parentElement;
            const content = faqItem.querySelector('.faq-content');
            const icon = this.querySelector('svg');
            
            // Close all other FAQs
            document.querySelectorAll('.faq-item').forEach(item => {
                if (item !== faqItem) {
                    item.querySelector('.faq-content').classList.add('hidden');
                    item.querySelector('svg').style.transform = 'rotate(0deg)';
                }
            });
            
            // Toggle current FAQ
            content.classList.toggle('hidden');
            icon.style.transform = content.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });
    
    // ROI Calculator
    const hoursInput = document.getElementById('hours-input');
    const rateInput = document.getElementById('rate-input');
    const hoursDisplay = document.getElementById('hours-display');
    const rateDisplay = document.getElementById('rate-display');
    const savingsDisplay = document.getElementById('savings-display');
    const annualDisplay = document.getElementById('annual-display');
    
    function calculateROI() {
        const hours = parseInt(hoursInput.value);
        const rate = parseInt(rateInput.value);
        const monthly = hours * rate * 4; // 4 weeks
        const annual = monthly * 12;
        
        hoursDisplay.textContent = hours + ' hours';
        rateDisplay.textContent = '$' + rate + '/hour';
        savingsDisplay.textContent = '$' + monthly.toLocaleString();
        annualDisplay.textContent = '$' + annual.toLocaleString();
    }
    
    if (hoursInput && rateInput) {
        hoursInput.addEventListener('input', calculateROI);
        rateInput.addEventListener('input', calculateROI);
        calculateROI(); // Initial calculation
    }
    
    // Contact form. Everything about where an enquiry goes lives in
    // js/enquiry.js so that the three forms on this site cannot drift apart.
    const topicLabel = (form) => {
        const select = form.elements.service;
        if (!select || select.selectedIndex < 0) return '';
        return select.options[select.selectedIndex].text.trim();
    };

    AutoFlowEnquiry.wire({
        formId: 'contact-form',
        panelId: 'contact-sent',
        title: 'AutoFlow — enquiry from the website',
        subject: 'AutoFlow enquiry',
        rows: (form, field) => [
            ['Name', field(form, 'name')],
            ['Business', field(form, 'business')],
            ['Email', field(form, 'email')],
            ['Phone', field(form, 'phone')],
            ['Service asked about', topicLabel(form)],
            ['What wastes their time', field(form, 'message')],
        ],
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Navbar background on scroll
    const nav = document.querySelector('nav');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            nav.classList.add('shadow-md');
        } else {
            nav.classList.remove('shadow-md');
        }
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card-hover').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
});

// There used to be two commented-out blocks at the end of this file: a Formspree
// snippet pointing at an unconfigured form id, and an EmailJS snippet pointing at
// a placeholder public key. They were inert, but they were the reason a placeholder
// could live in this repository unnoticed — the file read as "just uncomment this
// later", so nobody noticed that the live path above threw every enquiry away
// instead. Enquiries now go through js/enquiry.js, configured in one place
// (ROUTING) and asserted by scripts/check-buy-path.mjs, which fails on placeholders.

