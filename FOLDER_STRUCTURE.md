# 📁 Ideal CMS Folder Structure

## ✅ Current Project Structure (After Refactoring)

```
d:\devotinal2\project/
│
├── 📄 manage.py
├── 📄 db.sqlite3
├── 📄 CMS_ARCHITECTURE.md  ← **READ THIS FIRST!**
│
├── 📁 myproject/           ← Django Settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── 📁 core/                ← Django App (Business Logic)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── services_data.py
│
├── 📁 static/              ← Static Files (CSS, JS, Images)
│   ├── css/
│   │   ├── style.css
│   │   ├── home.css
│   │   ├── videos.css
│   │   └── preloader.css
│   ├── js/
│   │   ├── cart.js
│   │   └── lightbox.js
│   ├── images/
│   │   ├── hero_graphic.png
│   │   ├── temple1.jpeg
│   │   ├── temple2.jpeg
│   │   ├── budha.jpg
│   │   └── ... (all images)
│   └── videos/
│       ├── snipping.mp4
│       └── om-[hindugodsongs.in].mp3.mpeg
│
└── 📁 templates/          ← **TEMPLATE SYSTEM**
    │
    ├── 📄 base.html       ← Master Template (DTL - Developers Only)
    │
    ├── 📁 pages/          ← **DTL WRAPPERS** (Developers Only)
    │   │                   Contains Django logic, URL routing, loops
    │   │
    │   ├── home.html
    │   ├── about.html
    │   ├── services.html
    │   ├── service_detail.html
    │   ├── contact.html
    │   ├── blogs.html
    │   ├── temples.html
    │   ├── cart.html
    │   ├── login.html
    │   ├── signup.html
    │   ├── purohit_dashboard.html
    │   ├── purohit_login.html
    │   └── purohit_signup.html
    │
    ├── 📁 includes/       ← **REUSABLE DTL COMPONENTS** (Developers Only)
    │   │                   Global components with Django logic
    │   │
    │   ├── navbar.html    ← Loads nav menu, handles active states
    │   ├── footer.html    ← Footer with dynamic links
    │   └── hero.html      ← Hero wrapper (includes CMS content)
    │
    ├── 📁 cms/            ← **🎯 ADMIN-EDITABLE ZONE** (HTML Only!)
    │   │                   ⚠️  NO Django tags allowed here!
    │   │                   ✅  Pure HTML, CSS, JavaScript only
    │   │
    │   ├── 📁 home/       ← Home Page Content
    │   │   ├── hero_content.html
    │   │   ├── services_grid.html
    │   │   ├── stats_section.html
    │   │   ├── how_it_works.html
    │   │   ├── authentic_divine.html
    │   │   ├── videos_section.html
    │   │   └── testimonials.html
    │   │
    │   ├── 📁 about/      ← About Page Content
    │   │   ├── hero_content.html
    │   │   ├── mission_section.html
    │   │   └── values_grid.html
    │   │
    │   ├── 📁 services/   ← Services Page Content
    │   │   ├── services_list.html
    │   │   └── service_detail_content.html
    │   │
    │   ├── 📁 contact/    ← Contact Page Content
    │   │   └── contact_form.html
    │   │
    │   ├── 📁 temples/    ← Temples Page Content
    │   │   └── temples_grid.html
    │   │
    │   └── 📁 blogs/      ← Blogs Page Content
    │       └── blogs_grid.html
    │
    └── 📁 content/        ← ❌ OLD FOLDER (To be deprecated)
                            Mixed DTL+HTML - confusing for admins
                            Will be deleted after migration complete
```

---

## 🔐 Access Control

### 👨‍💻 **Developers Can Edit:**
- `templates/base.html`
- `templates/pages/*.html`  
- `templates/includes/*.html`
- `core/*.py`
- `myproject/*.py`

### 🎨 **Admins Can Edit:**
- `templates/cms/**/*.html` ← **ONLY THIS FOLDER!**
- `static/images/` (adding/replacing images)
- `static/videos/` (adding/replacing videos)

---

## 🎯 How the System Works

### Example: Home Page Request

**1. User visits:** `https://yoursite.com/`

**2. Django routes to:** `core/views.py` → `home()` function

**3. Django loads:** `templates/pages/home.html`  
```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
  {% include 'cms/home/hero_content.html' %}      ← Pure HTML
  {% include 'cms/home/services_grid.html' %}     ← Pure HTML
  {% include 'cms/home/stats_section.html' %}     ← Pure HTML
  ...
{% endblock %}
```

**4. Each `{% include %}` pulls in admin-editable HTML**

**5. Admin safely edits:** `templates/cms/home/hero_content.html`

**6. Changes appear on refresh** (no deployment needed)

---

## 📝 File Naming Convention

### Pages Wrapper (DTL)
**Location:** `templates/pages/`  
**Format:** `{page_name}.html`  
**Examples:**
- `home.html`
- `about.html`
- `services.html`
- `contact.html`

### CMS Content (Pure HTML)
**Location:** `templates/cms/{page_name}/`  
**Format:** `{section}_content.html` or `{section}.html`  
**Examples:**
- `cms/home/hero_content.html`
- `cms/home/services_grid.html`
- `cms/about/mission_section.html`
- `cms/services/services_list.html`

---

## 🚦 Migration Status

### ✅ **Completed:**
- [x] Created `CMS_ARCH ITECTURE.md` documentation
- [x] Created `templates/cms/` folder structure
- [x] Migrated Home page to new structure:
  - [x] `cms/home/hero_content.html`
  - [x] `cms/home/services_grid.html`
  - [x] `cms/home/stats_section.html`
  - [x] `cms/home/how_it_works.html`
  - [x] `cms/home/authentic_divine.html`
  - [x] `cms/home/videos_section.html`
  - [x] `cms/home/testimonials.html`
- [x] Refactored `templates/pages/home.html` wrapper
- [x] Refactored `templates/includes/hero.html` wrapper

### ⏳ **Pending:**
- [ ] Migrate About page
- [ ] Migrate Services page
- [ ] Migrate Contact page
- [ ] Migrate Temples page
- [ ] Migrate Blogs page
- [ ] Migrate Login/Signup pages
- [ ] Migrate Cart page
- [ ] Migrate Purohit portal pages
- [ ] Delete old `templates/content/` folder
- [ ] Clean up `__pycache__` folders
- [ ] Remove obsolete `.pyc` files

---

## 🛠️ Next Steps for Developer

### 1. Test Current Changes
```bash
python manage.py runserver
```
Visit: `http://localhost:8000/` and verify home page works

### 2. Complete Migration
Convert remaining pages following the same pattern:

**For each page:**
1. Open `templates/content/{page}_content.html`
2. Remove all Django tags (`{% %}`, `{{ }}`)
3. Replace `{% url 'name' %}` with `/absolute/path/`
4. Replace `{% static 'path' %}` with `/static/path`
5. Save to `templates/cms/{page}/{section}.html`
6. Update `templates/pages/{page}.html` to include CMS files

### 3. Clean Up
```bash
# Delete old content folder after testing
Remove-Item -Path "d:\devotinal2\project\templates\content" -Recurse -Force

# Clean Python cache
Get-ChildItem -Path "d:\devotinal2\project" -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force
```

---

## 📞 Support Contacts

**For Technical Issues:**
- Developer: [Your Name/Email]
- Architecture Questions: See `CMS_ARCHITECTURE.md`

**For Content Editing:**
- Admin Portal: [Future Implementation]
- Manual Editing: Only edit files in `templates/cms/`
- Never touch files with `{% %}` or `{{ }}` tags

---

## ✨ Benefits of This Structure

| Benefit | Description |
|---------|-------------|
| **Safe Admin Editing** | Admins can't accidentally break Django logic |
| **Clear Separation** | Content vs Code boundaries are crystal clear |
| **Easy Maintenance** | Developers handle logic, admins handle content |
| **Version Control** | Track content changes separately from code |
| **Scalability** | Add new sections easily without touching Python |
| **No Training Needed** | Admins use familiar HTML/CSS only |
| **Instant Updates** | Changes appear on page refresh |
| **Error Prevention** | No risk of TemplateSyntaxError from admin edits |

---

## 🔍 Quick Reference

### Find a Section to Edit

**Want to edit home page hero?**  
→ `templates/cms/home/hero_content.html`

**Want to edit services grid on home page?**  
→ `templates/cms/home/services_grid.html`

**Want to edit about page mission?**  
→ `templates/cms/about/mission_section.html` (create if not exists)

**Want to add dynamic data (from database)?**  
→ Contact developer to update `templates/pages/{page}.html`

---

**Last Updated:** February 10, 2026  
**Version:** 1.0  
**Status:** Home Page Migrated ✅  
**Next:** Complete remaining pages migration
