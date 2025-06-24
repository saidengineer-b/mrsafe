continue /* Base Styles */
:root {
    --primary-color: #e63946; /* Safety red */
    --secondary-color: #457b9d; /* Safety blue */
    --accent-color: #f4a261; /* Safety orange */
    --dark-color: #1d3557;
    --light-color: #f1faee;
    --success-color: #2a9d8f; /* Safety green */
    --warning-color: #e9c46a; /* Safety yellow */
    --danger-color: #e63946;
    --gray-light: #f8f9fa;
    --gray-medium: #e9ecef;
    --gray-dark: #6c757d;
    --white: #ffffff;
    --black: #212529;
    --font-primary: 'Open Sans', sans-serif;
    --font-secondary: 'Roboto', sans-serif;
    --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-primary);
    color: var(--black);
    line-height: 1.6;
    background-color: var(--white);
}

h1, h2, h3, h4 {
    font-family: var(--font-secondary);
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
}

p {
    margin-bottom: 1rem;
}

a {
    text-decoration: none;
    color: inherit;
    transition: var(--transition);
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    border-radius: var(--border-radius);
    font-weight: 600;
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
    border: none;
}

.btn-primary {
    background-color: var(--primary-color);
    color: var(--white);
}

.btn-primary:hover {
    background-color: #c1121f;
    transform: translateY(-2px);
    box-shadow: var(--box-shadow);
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: var(--white);
}

.btn-secondary:hover {
    background-color: #315f7d;
    transform: translateY(-2px);
    box-shadow: var(--box-shadow);
}

.btn-large {
    padding: 15px 30px;
    font-size: 1.1rem;
}

.section-description {
    font-size: 1.1rem;
    color: var(--gray-dark);
    max-width: 700px;
    margin: 0 auto 2rem;
    text-align: center;
}

/* Safety Alert Bar */
.safety-alert {
    background-color: var(--warning-color);
    color: var(--black);
    padding: 8px 0;
    text-align: center;
    font-weight: 600;
    font-size: 0.9rem;
}

.safety-alert i {
    margin-right: 8px;
}

/* Header */
.header {
    padding: 20px 0;
    position: sticky;
    top: 0;
    background-color: var(--white);
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo img {
    height: 50px;
    width: auto;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 25px;
}

.nav-links a {
    font-weight: 600;
    color: var(--dark-color);
}

.nav-links a:hover {
    color: var(--primary-color);
}

.mobile-menu-btn {
    display: none;
    font-size: 1.5rem;
    cursor: pointer;
}

/* Hero Banner */
.hero-banner {
    padding: 80px 0;
    background: linear-gradient(135deg, var(--light-color) 0%, var(--white) 100%);
}

.hero-content {
    max-width: 600px;
}

.hero-content h1 {
    font-size: 2.8rem;
    margin-bottom: 1.5rem;
    color: var(--dark-color);
}

.hero-content .subtitle {
    font-size: 1.2rem;
    color: var(--gray-dark);
    margin-bottom: 2rem;
}

.cta-buttons {
    display: flex;
    gap: 15px;
    margin-top: 2rem;
}

.hero-image img {
    max-width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

/* Video Section */
.video-section {
    padding: 80px 0;
    text-align: center;
    background-color: var(--gray-light);
}

.video-container {
    max-width: 800px;
    margin: 0 auto;
}

.video-wrapper {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

.video-wrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

/* Features Section */
.features-section {
    padding: 80px 0;
    text-align: center;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
}

.feature-card {
    background-color: var(--white);
    padding: 30px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    transition: var(--transition);
    text-align: left;
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 20px;
    color: var(--white);
}

.safety-red { background-color: var(--primary-color); }
.safety-orange { background-color: var(--accent-color); }
.safety-yellow { background-color: var(--warning-color); }
.safety-green { background-color: var(--success-color); }
.safety-blue { background-color: var(--secondary-color); }
.safety-purple { background-color: #6a4c93; }

.feature-card h3 {
    margin-bottom: 15px;
    color: var(--dark-color);
}

/* How It Works Section */
.how-it-works {
    padding: 80px 0;
    background-color: var(--gray-light);
}

.steps-container {
    max-width: 800px;
    margin: 40px auto 0;
}

.step {
    display: flex;
    margin-bottom: 40px;
    align-items: flex-start;
}

.step-number {
    background-color: var(--primary-color);
    color: var(--white);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 20px;
    flex-shrink: 0;
}

.step-content {
    flex-grow: 1;
}

.step-content h3 {
    color: var(--dark-color);
}

.demo-cta {
    text-align: center;
    margin-top: 50px;
}

/* Report Example Section */
.report-example {
    padding: 80px 0;
}

.report-container {
    background-color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    overflow: hidden;
    margin-top: 40px;
}

.report-tabs {
    display: flex;
    border-bottom: 1px solid var(--gray-medium);
}

.tab {
    padding: 15px 25px;
    cursor: pointer;
    font-weight: 600;
    color: var(--gray-dark);
    border-bottom: 3px solid transparent;
    transition: var(--transition);
}

.tab.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.tab:hover:not(.active) {
    color: var(--dark-color);
}

.report-content {
    padding: 30px;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.tab-content ul {
    list-style: none;
}

.tab-content li {
    margin-bottom: 10px;
    padding-left: 30px;
    position: relative;
}

.tab-content li i {
    position: absolute;
    left: 0;
    top: 3px;
    font-size: 1.2rem;
}

.tab-content li i.fa-check-circle {
    color: var(--success-color);
}

.tab-content li i.fa-exclamation-triangle {
    color: var(--warning-color);
}

.tab-content li i.fa-clipboard-list {
    color: var(--secondary-color);
}

/* Testimonials Section */
.testimonials {
    padding: 80px 0;
    background-color: var(--gray-light);
    text-align: center;
}

.testimonial-slider {
    max-width: 800px;
    margin: 40px auto;
    position: relative;
    overflow: hidden;
}

.testimonial {
    display: none;
    padding: 40px;
    background-color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

.testimonial.active {
    display: block;
}

.quote {
    font-size: 1.2rem;
    font-style: italic;
    margin-bottom: 30px;
    position: relative;
}

.quote::before,
.quote::after {
    content: '"';
    font-size: 2rem;
    color: var(--gray-medium);
    position: absolute;
}

.quote::before {
    top: -15px;
    left: -20px;
}

.quote::after {
    bottom: -30px;
    right: -20px;
}

.author {
    display: flex;
    align-items: center;
    justify-content: center;
}

.author-image {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: var(--gray-medium);
    margin-right: 15px;
    background-size: cover;
    background-position: center;
}

.author-info h4 {
    margin-bottom: 5px;
    color: var(--dark-color);
}

.author-info p {
    color: var(--gray-dark);
    font-size: 0.9rem;
}

.testimonial-dots {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--gray-medium);
    margin: 0 5px;
    cursor: pointer;
    transition: var(--transition);
}

.dot.active {
    background-color: var(--primary-color);
    transform: scale(1.2);
}

/* CTA Section */
.cta-section {
    padding: 80px 0;
    text-align: center;
}

.cta-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
}

.cta-card {
    background-color: var(--white);
    padding: 40px 30px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    position: relative;
    transition: var(--transition);
}

.cta-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.cta-card.highlighted {
    border: 2px solid var(--primary-color);
}

.popular-badge {
    position: absolute;
    top: -15px;
    right: 20px;
    background-color: var(--primary-color);
    color: var(--white);
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.cta-card h3 {
    margin-bottom: 15px;
    color: var(--dark-color);
}

.cta-card p {
    margin-bottom: 25px;
    color: var(--gray-dark);
}

/* Contact Section */
.contact-section {
    padding: 80px 0;
    background-color: var(--gray-light);
}

.contact-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 50px;
    margin-top: 40px;
}

.contact-info {
    padding-right: 30px;
}

.contact-methods {
    margin-top: 30px;
}

.contact-method {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.contact-method i {
    font-size: 1.5rem;
    color: var(--primary-color);
    margin-right: 15px;
    width: 30px;
    text-align: center;
}

.contact-form {
    background-color: var(--white);
    padding: 40px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

.form-group {
    margin-bottom: 20px;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid var(--gray-medium);
    border-radius: var(--border-radius);
    font-family: var(--font-primary);
    transition: var(--transition);
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(230, 57, 70, 