{% block content %}
<!-- markdownlint-disable line-length no-inline-html -->
<!--
    line-length: Split up badges lines are busier than having long lines
    no-inline-html: We need that sweet center align
-->

<p align="center">
<br>
<img width="200" src="awesome-italia.png" alt="logo of awesome-italia">
<br>
</p>

{% for group in groups -%}
[{{group.icon}} {{group.name}}](#-{{group.slug}}) •&nbsp;
{%- endfor %}

<p align="center">
<a href="https://developers.italia.it/en/to-do" title="Search issues in need for help" >
    <strong>Want to help?</strong>
</a>
•
<a href="https://come-partecipo.italia.it"
    title="Scopri come contribuire al miglioramento dei servizi pubblici digitali del Paese"
>
    <strong>Come partecipo?</strong>
</a>
</p>

# Awesome Italia

> The organized list of awesome @italia (and friends) projects

{% for group in groups %}
## {{group.icon}} {{group.name}}

{% for repo in group.repos %}
- [{{repo.slug}}](https://github.com/italia/{{repo.slug}})
<img align="right" src="https://img.shields.io/github/stars/italia/{{repo.slug}}?label=%E2%AD%90%EF%B8%8F&logo=github" alt="GitHub stars">
<img align="right" src="https://img.shields.io/github/issues/italia/{{repo.slug}}" alt="GitHub issues">
{{repo.description}}
{% endfor %}
{% endfor %}

{% endblock %}
