{%- set core_layers = layers | selectattr('view') | list -%}
{%- set segments = core_layers | map(attribute='segment') | unique | list -%}
{%- set cn_nums = '〇一二三四五六七八九十' -%}
## {{ branches[0].code }}. {{ branches[0].name_short }} — 全栈总览（{{ core_layers | length }} 层）

按"{{ segments | join(' → ') }}"{{ cn_nums[segments | length] }}大段组织。

| 段 | 层号 | 层名 | 自然视角 / 解决的事 |
| --- | --- | --- | --- |
{%- set ns = namespace(prev='') %}
{%- for lyr in core_layers %}
|{% if lyr.segment != ns.prev %} {{ lyr.segment }}{% endif %} | {{ lyr.code }} | {{ (section_heading[lyr.code] | replace(lyr.code ~ ' ', '', 1)) if lyr.code in section_heading else lyr.name }} | {{ lyr.view }} |
{%- if ns.prev != lyr.segment %}{%- set ns.prev = lyr.segment %}{%- endif %}
{%- endfor %}

---
