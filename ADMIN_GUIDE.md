# 🎨 Admin Guide - How to Edit Website Content

## 👋 Welcome, Admin!

This guide will teach you how to safely edit website content without breaking anything.

---

## 🎯 What You Can Edit

You can ONLY edit files in this folder:
```
templates/cms/
```

**Example:**
- ✅ `templates/cms/home/hero_content.html` ← You CAN edit this
- ❌ `templates/pages/home.html` ← DON'T edit this (developer file)
- ❌ `core/views.py` ← NEVER edit this (Python code)

---

## 📂 Where to Find Content

### Home Page
```
templates/cms/home/
├── hero_content.html          ← Hero banner with slider
├── services_grid.html         ← Pooja services cards
├── stats_section.html         ← Mantra chakra & categories
├── how_it_works.html          ← 4-step process
├── authentic_divine.html      ← Why choose us section
├── videos_section.html        ← Video reels
└── testimonials.html          ← Client testimonials
```

### Other Pages
```
templates/cms/
├── about/      ← About page content
├── services/   ← Services page content
├── contact/    ← Contact page content
├── temples/    ← Temples page content
└── blogs/      ← Blogs page content
```

---

## ✅ What You CAN Do

### 1. Change Text
```html
<!-- BEFORE -->
<h1>Online Pooja Booking Platform</h1>

<!-- AFTER -->
<h1>Online Pooja Services</h1>
```

### 2. Change Images
```html
<!-- BEFORE -->
<img src="/static/images/hero1.jpg" alt="Hero">

<!-- AFTER -->
<img src="/static/images/new_hero.jpg" alt="Hero">
```
**Note:** First upload `new_hero.jpg` to `static/images/` folder

### 3. Change Links
```html
<!-- BEFORE -->
<a href="/services/">View Services</a>

<!-- AFTER -->
<a href="/puja-services/">View Puja Services</a>
```

### 4. Change Colors
```html
<!-- BEFORE -->
<section style="background-color: #ff0000;">

<!-- AFTER -->
<section style="background-color: #00ff00;">
```

### 5. Add/Remove HTML Elements
```html
<!-- Add a new paragraph -->
<p>New paragraph text here</p>

<!-- Add a new button -->
<a href="/contact/" class="btn">Contact Us</a>
```

---

## ❌ What You CANNOT Do

### 1. ❌ Use Django Template Tags
```html
<!-- DON'T DO THIS - Will cause errors! -->
{% load static %}
{% url 'home' %}
{{ variable_name }}
{% for item in items %}
{% if condition %}
```

### 2. ❌ Use Template Variables
```html
<!-- DON'T DO THIS -->
<h3>{{ service.name }}</h3>
<img src="{{ image.url }}">
```

### 3. ❌ Edit Developer Files  
**Never edit these:**
- `templates/pages/*.html`
- `templates/base.html`
- `core/*.py`
- `myproject/*.py`

---

## 📝 Step-by-Step: How to Edit

### Example: Change Home Page Hero Title

**Step 1:** Open file
```
File: d:\devotinal2\project\templates\cms\home\hero_content.html
```

**Step 2:** Find the line
```html
<h1>Online Pooja<br>Booking Platform</h1>
```

**Step 3:** Edit the text
```html
<h1>Divine Pooja<br>Services Online</h1>
```

**Step 4:** Save the file

**Step 5:** Refresh your browser  
Changes should appear immediately!

---

## 🖼️ How to Add Images

### Step 1: Upload Image
1. Copy your image file (e.g., `new_image.jpg`)
2. Paste it into: `d:\devotinal2\project\static\images\`

### Step 2: Use in HTML
```html
<img src="/static/images/new_image.jpg" alt="Description">
```

### Step 3: Save & Refresh
Your image should now appear on the page!

---

## 🎨 How to Change Colors

### Method 1: Inline Styles
```html
<section style="background-color: #ff5733; color: #ffffff;">
  <h2 style="color: #ffd700;">Golden Heading</h2>
</section>
```

### Method 2: CSS Classes (in same file)
```html
<style>
.my-section {
  background-color: #ff5733;
  color: #ffffff;
  padding: 40px;
}
</style>

<section class="my-section">
  Content here
</section>
```

---

## 🔗 How to Change Links

### Internal Links (within website)
```html
<!-- Link to services page -->
<a href="/services/">View Services</a>

<!-- Link to about page -->
<a href="/about/">About Us</a>

<!-- Link to contact page -->
<a href="/contact/">Contact Us</a>
```

### External Links
```html
<!-- Link to external website -->
<a href="https://example.com" target="_blank">External Link</a>
```

---

## 🚨 Common Mistakes to Avoid

### Mistake 1: Forgetting Closing Tags
```html
<!-- ❌ WRONG - Missing </div> -->
<div class="container">
  <h2>Title</h2>

<!-- ✅ CORRECT -->
<div class="container">
  <h2>Title</h2>
</div>
```

### Mistake 2: Using Wrong Quote Marks
```html
<!-- ❌ WRONG - Curly quotes -->
<img src="image.jpg" alt="Photo">

<!-- ✅ CORRECT - Straight quotes -->
<img src="image.jpg" alt="Photo">
```

### Mistake 3: Breaking Image Paths
```html
<!-- ❌ WRONG - Missing /static/ prefix -->
<img src="images/photo.jpg">

<!-- ✅ CORRECT -->
<img src="/static/images/photo.jpg">
```

---

## 🧪 How to Test Your Changes

### 1. Save the file
Press `Ctrl + S` to save

### 2. Go to your browser
Open your website (e.g., `http://localhost:8000/`)

### 3. Hard refresh
Press `Ctrl + F5` to force refresh (clears cache)

### 4. Check the page
Look for your changes

### If changes don't appear:
1. Make sure you saved the correct file
2. Clear browser cache (`Ctrl + Shift + Delete`)
3. Restart Django server (ask developer)

---

## 🆘 What to Do If Something Breaks

### Symptom: Page shows error
**Likely cause:** Used Django template tags accidentally

**Solution:**
1. Open the file you just edited
2. Remove any `{% %}` or `{{ }}` tags
3. Use plain HTML instead
4. Save and refresh

### Symptom: Image doesn't show
**Likely cause:** Wrong image path

**Solution:**
1. Check if image exists in `static/images/`
2. Make sure path starts with `/static/`
3. Check for typos in filename

### Symptom: Layout looks broken
**Likely cause:** Deleted important HTML tag

**Solution:**
1. Undo your changes (`Ctrl + Z`)
2. Make changes more carefully
3. Ask developer for help

---

## 📞 When to Contact Developer

Contact the developer if you need to:
- Add dynamic content from database
- Create loops (repeat content for each item)
- Add conditional logic (show/hide based on conditions)
- Change URL routing
- Modify navigation menu
- Change page structure significantly

---

## ✅ Checklist Before Saving

Before saving any file, verify:
- [ ] No Django tags (`{% %}`, `{{ }}`)
- [ ] All HTML tags are properly closed
- [ ] Image paths start with `/static/`
- [ ] Links are correct
- [ ] No syntax errors (matching quotes, brackets)
- [ ] File is saved in `templates/cms/` folder

---

## 🎓 HTML Quick Reference

### Basic Tags
```html
<!-- Headings -->
<h1>Main Heading</h1>
<h2>Sub Heading</h2>
<h3>Section Heading</h3>

<!-- Paragraphs -->
<p>Regular paragraph text</p>

<!-- Links -->
<a href="/page/">Link Text</a>

<!-- Images -->
<img src="/static/images/photo.jpg" alt="Description">

<!-- Buttons -->
<a href="/page/" class="btn">Button</a>

<!-- Containers -->
<div class="container">
  Content here
</div>

<section class="section-name">
  Section content
</section>
```

### Icons (FontAwesome)
```html
<i class="fas fa-home"></i>        <!-- Home icon -->
<i class="fas fa-star"></i>        <!-- Star icon -->
<i class="fas fa-heart"></i>       <!-- Heart icon -->
<i class="fas fa-phone"></i>       <!-- Phone icon -->
<i class="fas fa-envelope"></i>    <!-- Email icon -->
```

---

## 📚 More Help

**Read these documents:**
1. `CMS_ARCHITECTURE.md` - Full technical documentation
2. `FOLDER_STRUCTURE.md` - Complete folder structure guide

**Online Resources:**
- HTML Tutorial: https://www.w3schools.com/html/
- CSS Tutorial: https://www.w3schools.com/css/

---

## 🎉 You're Ready!

You now know how to:
- ✅ Find and edit content files
- ✅ Change text, images, and colors
- ✅ Avoid common mistakes
- ✅ Test your changes
- ✅ Fix basic errors

**Happy editing! 🚀**

---

**Last Updated:** February 2026  
**For Support:** Contact your developer  
**Safe Editing Zone:** `templates/cms/` only!
