# CMS Architecture - Admin-Friendly Template System

## 📋 Overview
This project follows a **CMS-style architecture** where:
- **Django Template Logic (DTL)** is kept separate in wrapper files
- **Pure HTML content** is isolated for safe admin editing
- **No mixing** of Python/Django code with content HTML

---

## 📁 Folder Structure

```
project/
├── templates/
│   ├── base.html                 ← Master template (DTL - DO NOT EDIT)
│   │
│   ├── pages/                    ← Page wrappers (DTL only)
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── services.html
│   │   ├── service_detail.html
│   │   ├── contact.html
│   │   ├── blogs.html
│   │   ├── temples.html
│   │   ├── cart.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── purohit_*.html
│   │
│   ├── includes/                 ← Reusable DTL components
│   │   ├── navbar.html           (DTL - loads dynamic data)
│   │   ├── footer.html           (DTL - loads dynamic data)
│   │   └── hero.html             (DTL wrapper)
│   │
│   └── cms/                      ← 🎯 ADMIN-EDITABLE ZONE
│       ├── home/
│       │   ├── hero_content.html
│       │   ├── services_grid.html
│       │   ├── stats_section.html
│       │   ├── how_it_works.html
│       │   ├── testimonials.html
│       │   └── videos_section.html
│       │
│       ├── about/
│       │   ├── hero_content.html
│       │   ├── mission_section.html
│       │   └── values_grid.html
│       │
│       ├── services/
│       │   ├── services_list.html
│       │   └── service_detail_content.html
│       │
│       ├── contact/
│       │   └── contact_form.html
│       │
│       ├── temples/
│       │   └── temples_grid.html
│       │
│       └── blogs/
│           └── blogs_grid.html
```

---

## 🔐 File Types Explained

### 1. **DTL Wrapper Files** (Developer Zone - Contains Django Code)
**Location:** `templates/pages/*.html`, `templates/includes/*.html`

**Purpose:** Handle Django logic, URL routing, data passing

**Contains:**
- `{% extends 'base.html' %}`  
- `{% load static %}`
- `{% url 'page-name' %}`
- `{% for item in items %}`
- `{% if condition %}`
- `{% include 'cms/...' %}`

**Example:** `templates/pages/home.html`
```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
  <!-- Hero Section -->
  {% include 'cms/home/hero_content.html' %}
  
  <!-- Services Section -->
  {% include 'cms/home/services_grid.html' %}
  
  <!-- Stats Section -->
  {% include 'cms/home/stats_section.html' %}
{% endblock %}
```

---

### 2. **Pure HTML Content Files** (Admin Zone - HTML Only)
**Location:** `templates/cms/**/*.html`

**Purpose:** Contain only page content that admins can safely edit

**Contains ONLY:**
- Valid HTML tags (`<div>`, `<section>`, `<h1>`, `<p>`, etc.)
- Static text content
- Image paths (static URLs already processed)
- CSS classes (no inline Django)
- JavaScript (optional, for interactivity)

**CANNOT Contain:**
- ❌ `{% load static %}`
- ❌ `{% url 'name' %}`
- ❌ `{% for %}`
- ❌ `{% if %}`
- ❌ `{{ variable }}`
- ❌ Any Python code

**Example:** `templates/cms/home/hero_content.html`
```html
<!-- Hero Section - Pure HTML -->
<section class="hero-section">
  <div class="container">
    <div class="hero-slider">
      <div class="hero-slide active">
        <img src="/static/images/hero1.jpg" alt="Divine Puja Services">
        <div class="hero-content">
          <h1>Welcome to Divine Blessings</h1>
          <p>Book authentic Vedic puja services online</p>
          <a href="/services/" class="btn">Explore Services</a>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
/* Hero section styles */
.hero-section {
  background: linear-gradient(135deg, #b30000, #661414);
  padding: 80px 0;
}
.hero-content h1 {
  color: #f5b700;
  font-size: 48px;
}
</style>

<script>
// Hero slider logic
document.addEventListener('DOMContentLoaded', function() {
  const slides = document.querySelectorAll('.hero-slide');
  let currentSlide = 0;
  
  setInterval(() => {
    slides[currentSlide].classList.remove('active');
    currentSlide = (currentSlide + 1) % slides.length;
    slides[currentSlide].classList.add('active');
  }, 5000);
});
</script>
```

---

## 🎯 Key Principles

### ✅ DO in CMS Files (Admin-Editable):
1. Use standard HTML tags
2. Use hardcoded URLs (e.g., `/services/`, `/about/`)
3. Use `/static/` prefix for images
4. Add CSS in `<style>` tags
5. Add JavaScript in `<script>` tags
6. Modify text content freely
7. Change images, colors, layout

### ❌ DON'T in CMS Files:
1. Use Django template tags (`{% %}`)
2. Use Django variables (`{{ }}`)
3. Load static files with `{% static %}`
4. Use URL tags (`{% url %}`)
5. Use for loops or if statements
6. Import Django templatetags

---

## 🔄 How It Works

### Example Flow: Home Page

**1. User visits:** `https://yoursite.com/`

**2. Django loads:** `templates/pages/home.html`
```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
  {% include 'cms/home/hero_content.html' %}
  {% include 'cms/home/services_grid.html' %}
  {% include 'cms/home/stats_section.html' %}
{% endblock %}
```

**3. Each `{% include %}` loads pure HTML from `cms/` folder**

**4. Admin edits:** `templates/cms/home/hero_content.html` (safely!)

**5. Page refreshes:** Changes appear immediately

---

## 📝 Admin Editing Guide

### Safe Editing Checklist ✅

**Before editing any file in `templates/cms/`:**

1. ✅ **Use HTML tags only**
   ```html
   <div class="section">
     <h2>My Heading</h2>
     <p>My paragraph</p>
   </div>
   ```

2. ✅ **Use absolute paths for links**
   ```html
   <a href="/services/">View Services</a>
   <a href="/about/">About Us</a>
   ```

3. ✅ **Use /static/ for images**
   ```html
   <img src="/static/images/hero.jpg" alt="Hero">
   ```

4. ✅ **Inline CSS is OK**
   ```html
   <style>
   .my-section { background: #f5b700; }
   </style>
   ```

5. ✅ **JavaScript is OK**
   ```html
   <script>
   document.getElementById('myBtn').onclick = function() {
     alert('Clicked!');
   };
   </script>
   ```

---

### What NOT to Do ❌

**DON'T use Django syntax:**
```html
<!-- ❌ BAD - Will cause errors -->
{% load static %}
<img src="{% static 'images/hero.jpg' %}" alt="Hero">
<a href="{% url 'services' %}">Services</a>
{{ service.name }}
{% for item in items %}...{% endfor %}
```

**Instead, use:**
```html
<!-- ✅ GOOD - Safe HTML -->
<img src="/static/images/hero.jpg" alt="Hero">
<a href="/services/">Services</a>
<h3>Ganesh Puja</h3>
<!-- Repeat manually for each item -->
```

---

## 🛠️ Developer Zone

### When to Edit DTL Wrappers (Developers Only)

**Edit `templates/pages/*.html` when:**
- Adding new sections with dynamic data
- Changing page structure/order
- Adding loops (`{% for %}`)
- Adding conditions (`{% if %}`)
- Passing Django context variables
- Integrating database queries

**Example:**
```django
<!-- templates/pages/services.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
  <!-- Static hero content -->
  {% include 'cms/services/hero.html' %}
  
  <!-- Dynamic services list -->
  <section class="services-list">
    <div class="container">
      {% for service in services %}
        <div class="service-card">
          <h3>{{ service.name }}</h3>
          <p>{{ service.description }}</p>
          <a href="{% url 'service_detail' service.slug %}">View Details</a>
        </div>
      {% endfor %}
    </div>
  </section>
  
  <!-- Static CTA content -->
  {% include 'cms/services/cta_section.html' %}
{% endblock %}
```

---

## 🚨 Error Prevention

### Common Errors & Fixes

#### Error 1: `TemplateSyntaxError`
**Cause:** Django template tag in CMS file

```html
<!-- ❌ In templates/cms/home/hero.html -->
{% load static %}
<img src="{% static 'images/hero.jpg' %}">
```

**Fix:** Remove DTL syntax
```html
<!-- ✅ Fixed -->
<img src="/static/images/hero.jpg">
```

---

#### Error 2: `TemplateDoesNotExist`
**Cause:** Wrong path in `{% include %}`

```django
<!-- ❌ In templates/pages/home.html -->
{% include 'content/hero_content.html' %}
```

**Fix:** Update path to cms folder
```django
<!-- ✅ Fixed -->
{% include 'cms/home/hero_content.html' %}
```

---

#### Error 3: Dynamic URLs broken
**Cause:** Hardcoded URLs changed

```html
<!-- If admin changes link -->
<a href="/services/">Services</a>
<!-- But Django URL is /puja-services/ -->
```

**Fix:** Developer updates wrapper to preserve link
```django
<!-- In templates/includes/navbar.html -->
<a href="{% url 'services' %}">Services</a>
```

---

## 📊 Migration Checklist

### Converting Existing Templates

#### Step 1: Identify DTL vs Content
**Open file:** `templates/content/services_content.html`

**Find DTL:**
- `{% load static %}` ← DTL
- `{% url 'name' %}` ← DTL  
- `<section>...<h2>` ← Content

#### Step 2: Create CMS File
**Create:** `templates/cms/home/services_grid.html`

**Copy only:** HTML content, remove all `{% %}` tags

#### Step 3: Replace URLs
**Replace:**
```html
<!-- OLD -->
<a href="{% url 'service_detail' service_slug='ganesh-homa' %}">

<!-- NEW -->
<a href="/services/ganesh-homa/">
```

#### Step 4: Update Wrapper
**Edit:** `templates/pages/home.html`

```django
<!-- OLD -->
{% include 'content/services_content.html' %}

<!-- NEW -->
{% include 'cms/home/services_grid.html' %}
```

---

## 📖 Quick Reference

### File Naming Convention

| File Type | Location | Naming | Example |
|-----------|----------|--------|---------|
| Page Wrapper | `templates/pages/` | `{page}.html` | `home.html` |
| Include Wrapper | `templates/includes/` | `{component}.html` | `navbar.html` |
| CMS Content | `templates/cms/{page}/` | `{section}_content.html` | `hero_content.html` |

### Standard CMS Sections

**For every page, create:**
1. `hero_content.html` - Hero/banner section
2. `main_content.html` - Main page content
3. `cta_section.html` - Call-to-action section

---

## 🎓 Training for Admins

### Admin Portal Setup (Future)

**Goal:** Allow admins to edit CMS files through web interface

**Features:**
1. File browser showing only `templates/cms/` folder
2. HTML editor with syntax highlighting
3. Live preview before saving
4. Version control (keep backup of changes)
5. Validation (ensure no Django tags used)

**Admin Workflow:**
1. Login to admin portal
2. Navigate to page section (e.g., Home > Hero)
3. Edit HTML in visual editor
4. Click "Preview" to see changes
5. Click "Publish" to go live
6. Page refreshes automatically

---

## 🔒 Security & Validation

### Pre-Save Validation

Before admin saves CMS file, check:
```python
# In admin portal backend
def validate_cms_html(html_content):
    forbidden_patterns = [
        r'{%',      # Django tags
        r'{{',      # Django variables  
        r'%}',      # Tag closures
        r'}}',      # Variable closures
    ]
    
    for pattern in forbidden_patterns:
        if pattern in html_content:
            raise ValidationError(
                f"Django template syntax not allowed. "
                f"Use only pure HTML."
            )
    
    return True
```

---

## 📞 Support

**For Admins:**
- Only edit files in `templates/cms/` folder
- Use HTML, CSS, JavaScript only
- Contact developer for dynamic data needs

**For Developers:**
- Edit `templates/pages/` for Django logic
- Update `templates/includes/` for global components
- Keep `templates/cms/` clean for admin editing

---

## ✨ Benefits

1. **Safe Admin Editing** - No risk of breaking Django logic
2. **Clear Separation** - Content vs Code boundaries
3. **Easy Maintenance** - Developers handle logic, admins handle content
4. **Version Control** - Track changes separately
5. **Scalability** - Add new sections easily
6. **No Training Needed** - Admins use familiar HTML only

---

**Last Updated:** February 2026  
**Architecture Version:** 2.0  
**Status:** Production Ready 🚀
