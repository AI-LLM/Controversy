## 各领域分支细节（{{ branches[1].code }}–{{ branches[-1].code }}，共享 {{ layers[0].code }}–L09，从 L10 起分叉）

{%- set non_a = branches | rejectattr('code', 'equalto', 'A') | list -%}
{%- set b_subs = sub_branches | selectattr('parent_code', 'equalto', branches[1].code) | list -%}
以下 {{ non_a | length }} 个领域分支（{% for br in non_a %}**{{ br.code }}** {{ br.name_short }}{% if not loop.last %} / {% endif %}{% endfor %}）共享 {{ layers[0].code }}–L09 通用 GPU 栈，从 L10 起在领域模型 / 数据 / 部署 / 终端产品上各自分叉。{{ branches[1].code }} 因为最早成形而拆出 {% for s in b_subs %}{{ s.code }}{% if not loop.last %} / {% endif %}{% endfor %} {{ ['一','二','三','四','五','六','七','八','九'][b_subs|length - 1] }}个子层；其余分支用数字后缀（{{ branches[2].code }}1 / {{ branches[2].code }}2 / …）继续切。A 分支无独立子层，其 L10+ 内容随 {{ layers[0].code }}–{{ layers[-1].code }} 各层段直接呈现。
