# SaaS-Bench → CLI-Anything 迁移分析

把 `chat/SaaS-Bench/` 的 106 个任务从依赖自托管 SaaS docker 镜像，重写为依赖 `chat/CLI-Anything/` 注册表中的 CLI。

## 工作产物

每个任务目录里：

- `description.md`：使用 CLI-Anything CLI 完成相同业务目标的新版任务说明（**已替换**）。
- `meta.json`：`sites` 改为 CLI 名字数组；新增 `cli_substitution = {original_sites, rationale}`；移除 `require_login`（CLI 用 env var）。（**已替换**）
- `description.saas.md`、`meta.saas.json`：原 SaaS 版本备份（**未动**）。
- `verify.py`：**未动**——原 verify 直接 `docker exec` 调用 SaaS 容器内 DB/API，CLI 替代后这些断言一律会失败。**这是已知风险**，本次未解决；要让 verify 通过需重写 verify.py 为读取 obsidian/calibre/chromadb/seaclip CLI 输出 + 文件断言（见末尾"verify.py 风险"）。

## 体量

| 类别 | 任务数 | 原 SaaS app | 主要 CLI 替代 |
|---|---:|---|---|
| Agriculture (multi-m) | 12 | e-label, grocy, recipya, farmos | libreoffice + anygen + obsidian + calibre |
| Media (multi-m) | 20 | watcharr, siyuan, booklore, photoprism, mediacms | obsidian + calibre + gimp + contentful |
| Business (uni-m) | 15 | twenty, bigcapital, hrms, pretix | contentful + firefly-iii + obsidian + libreoffice + shopify + mailchimp + n8n |
| Healthcare (uni-m) | 16 | openemr, opnform, onlyoffice | obsidian + anygen + libreoffice + py4csr + feishu + macrocli + n8n + mailchimp |
| Software (uni-m) | 31 | code-server, baserow, openproject, metabase | iterm2 + chromadb + seaclip + stata + libreoffice + n8n |
| Teamwork (uni-m) | 12 | mattermost, onlyoffice, owncloud, roundcubemail | feishu + libreoffice + obsidian + mailchimp |
| **合计** | **106** | **23 个 SaaS app** | **20+ 个 CLI-Anything CLI** |

## 整体替代映射

| 原 SaaS 类型 | 原 app | 主 CLI 替代 | 替代质量 |
|---|---|---|---|
| 葡萄酒数字标签 | e-label | libreoffice headless ODT→PDF + anygen QR | 中（无合规字段强校验） |
| 家庭库存 / 购物清单 | grocy | obsidian vault `inventory/<name>.md` frontmatter（qty/unit/batch_number/expiry）+ `shopping-list.md` markdown 清单 | 弱（无 typed schema、阈值告警、单位换算） |
| 食谱搜索 | recipya | calibre 库（食谱当一本"书"，custom column `#ingredients`、`#cuisine`、`#recipe_id`，cover 当 dish 图） | 中（关键词搜索可，但无 ingredient 结构化） |
| 农场资产/typed log | farmos | obsidian vault `assets/<asset>.md` + `logs/<date>-<type>.md` frontmatter（log_type/severity/omri_cert/attachments） | 弱（无 typed log/asset 类型、附件挂载、日期算术） |
| 影视追踪 | watcharr | obsidian `Watchlog/<film>.md` frontmatter（status, rating, review） | 中（无 TMDB 查询、时间线视图） |
| 笔记/知识库 | siyuan | obsidian vault（folder=notebook, .md=document, `## H2`=section, `[[wikilink]]`=反向链接） | 强（功能等价） |
| 电子书库 | booklore | calibre（list/search/metadata/conversion 几乎完美对应） | 强 |
| 照片库 | photoprism | calibre 当媒体库 + gimp/exiftool 读 EXIF | 弱（无 geo/face/auto-index） |
| 媒体 CMS | mediacms | contentful entry create + media upload + tags + publish | 中（无内置转码，串 videocaptioner/shotcut） |
| CRM | twenty | contentful 自定义 Content Type（Company/Person/Opportunity/Task/Note）+ obsidian | 中（pipeline stages、favorites、relations 全靠 link field） |
| 会计/财务 | bigcapital | firefly-iii bills/invoices/payments + libreoffice 报表 + n8n bank rules | 中（缺 items 目录、sales estimate、aging 桶、sales tax） |
| 人事 HR | hrms | obsidian `Employees/HR-EMP-NNNNN — Name.md` + YAML frontmatter + libreoffice 工资单 | 弱（无 leave/salary/appraisal/grievance/recruitment 工作流引擎） |
| 售票/活动 | pretix | shopify 商品+折扣码 + contentful 活动页 + mailchimp 受众 | 弱（缺 shared quota / check-in / tax rule / membership / voucher 分级） |
| 电子病历 | openemr | obsidian `Patients/<Name>/encounters/<date>.md` frontmatter（Vitals/Issues/Fee Sheet）+ sections（SOAP/Care Plan/Immunizations） | 弱（无 typed EHR、合并病人、Patient Flow Board、System Log、Billing Manager） |
| 表单 | opnform | anygen 生静态 HTML 表单 + n8n webhook | 中（缺 matrix/signature/video/code-block field、conditional logic 全靠 JS、theme/CSS） |
| 文档协作 | onlyoffice | libreoffice headless（DOCX/XLSX/PDF/PPTX 转换+openpyxl 图表） | 强（无 GUI 协作，但终态文件等价） |
| IM 团队聊天 | mattermost | feishu（Lark 官方 CLI；channel/message/bot 最接近） | 中（不是 1:1 SaaS 等价，但功能可映射） |
| 网盘 | owncloud | obsidian shared vault（文件 + 元数据） | 弱（无原生 webdav/分享链接/权限矩阵） |
| 邮箱客户端 | roundcubemail | mailchimp（发邮件/受众）；接收/IMAP 读取无 CLI 替代 | 弱（接收侧空缺） |
| 浏览器版 IDE | code-server | iterm2 + 本地 shell（rg/sed/git/find/awk） | 强 |
| 结构化数据库 | baserow | chromadb metadata（无 schema/单选/链接/视图） | **极弱**（最难凑） |
| 项目管理 | openproject | seaclip Kanban + Issue + Version | 中（缺 wiki/meeting/admin enum priorities） |
| BI | metabase | stata `.do` + `graph bar/pie/scatter` + libreoffice 拼装 dashboard ODP/PDF | 中（无 web 视图，离线脚本+静态图） |

## CLI-Anything 缺口 + 建议新建 CLI

按 `chat/CLI-Anything/CONTRIBUTING.md` 的 in-repo harness 规范：

### 1. `cli-anything-grocy-shim`（家庭库存）

- **路径**：`grocy/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=grocy/agent-harness`
- **entry_point**：`cli-anything-grocy`
- **核心命令**：
  - `product set --vault . --name <name> --qty <n> --unit <u> --batch <id> --expiry <date>`
  - `shopping add --vault . --item <name> --qty <n> --unit <u> --note <text>`
  - `stock check --vault . --item <name> --threshold <qty>`
  - `recipe link --vault . --recipe <id> --product <name>`
- **后端**：写 obsidian vault markdown（避免引入新存储），但暴露 typed CRUD
- **覆盖**：grocy stock/shopping_list/recipe entity、阈值告警、unit conversion

### 2. `cli-anything-farmos-shim`（农场记录）

- **路径**：`farmos/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=farmos/agent-harness`
- **entry_point**：`cli-anything-farmos`
- **核心命令**：
  - `asset add --type plant|equipment --name <name> --alias-zh <name>`
  - `log add --type observation|input|maintenance|harvest|activity --asset <name> --date <date> --notes <text> --attach <file> --severity <lvl> --omri-cert <id> --rate <rate> --operator <name> --equipment <name>`
  - `log list --asset <name> --type <type> --since <date>`
  - `harvest list --batch <id>`
- **后端**：obsidian vault；约束 frontmatter schema
- **覆盖**：typed log + asset 类型 + 附件 + OMRI cert + batch number

### 3. `cli-anything-elabel-shim`（葡萄酒电子标签）

- **路径**：`e-label/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=e-label/agent-harness`
- **entry_point**：`cli-anything-elabel`
- **核心命令**：
  - `wine create --producer <name> --vintage <yr> --aoc <region> --grape <var> --alcohol <pct> --volume <ml> --allergens <list> --batch <id>`（强校验 `%vol` 格式、allergen 非空、AOC 枚举）
  - `wine sensory --serving-temp <range> --glass <type> --pairings <list> --tasting <text>`
  - `wine export-pdf --with-qr --out <pdf>`
- **后端**：libreoffice + anygen 组合，但增加合规字段校验层
- **覆盖**：e-label 合规校验 + QR-PDF 一键导出

### 4. `cli-anything-recipya-shim`（食谱关键词搜索）

- **路径**：`recipya/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=recipya/agent-harness`
- **entry_point**：`cli-anything-recipya`
- **核心命令**：
  - `recipe search --library <calibre-lib> --keyword <kw>`
  - `recipe show --library <lib> --id <id>` → 输出 JSON 带 ingredients/steps/image
  - `recipe create --library <lib> --name <name> --ingredients <csv> --steps <text> --image <file>`
  - `recipe ingredients --library <lib> --recipe <name>`
- **后端**：calibre 库 + custom columns（包装 calibredb）

### 5. `cli-anything-watcharr-shim` 或 `cli-anything-watchlog`（影视追踪）

- **路径**：`watchlog/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=watchlog/agent-harness`
- **entry_point**：`cli-anything-watchlog`
- **核心命令**：
  - `entry add --vault <obsidian> --title <film> --year <yr> --tmdb-id <id>`
  - `entry set --vault <v> --title <t> --status Watching|Watched|Plan --rating <0-10> --review <text>`
  - `entry list --vault <v> --status <s> --year <yr>`
  - `lookup --query <text>` → TMDB 查询（需 TMDB API key）

### 6. `cli-anything-photo-shim`（照片库 / EXIF）

- **路径**：`photo/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=photo/agent-harness`
- **entry_point**：`cli-anything-photo`
- **核心命令**：
  - `photo import --library <dir> --recursive`
  - `photo tag --library <dir> --photo <file> --tags <csv>`
  - `photo favorite --library <dir> --photo <file>`
  - `photo exif --photo <file>` → JSON 包 datetime/geo/camera
  - `photo search --library <dir> --tag <t> --geo <bbox> --since <date>`
- **后端**：exiftool + sqlite 索引

### 7. `cli-anything-baserow-shim` 或 `cli-anything-airbase`（结构化数据库）

- **路径**：`baserow/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=baserow/agent-harness`
- **entry_point**：`cli-anything-baserow`
- **核心命令**：
  - `database create --name <db>`
  - `table create --db <db> --name <t> --schema <json>`（含 single-select/number/date/link field）
  - `row add/set/delete --table <t> --data <json>`
  - `view create --table <t> --kind grid|kanban|form --filter <json> --sort <json>`
  - `form publish --view <id>` → 公网 URL（含 anti-CSRF token）
- **后端**：sqlite（schema 校验）+ FastAPI（公网 form）
- **覆盖**：Software 类几乎所有任务的关键缺口

### 8. `cli-anything-metabase-shim` 或 `cli-anything-saiku`（轻 BI）

- **路径**：`metabase/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=metabase/agent-harness`
- **entry_point**：`cli-anything-metabase`
- **核心命令**：
  - `collection create --name <c>`
  - `question create --collection <c> --sql <sql> --viz bar|pie|scatter|scalar|table`
  - `dashboard create --name <d> --add <question-id> --layout <json>`
  - `dashboard export --id <d> --to pdf|png`
- **后端**：duckdb + matplotlib + libreoffice 拼 ODP

### 9. `cli-anything-twenty-shim` / `cli-anything-crm`（CRM）

- **路径**：`crm/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=crm/agent-harness`
- **entry_point**：`cli-anything-crm`
- **核心命令**：
  - `company create --name <n> --domain <d>`
  - `person create --name <n> --company <c> --email <e>`
  - `opportunity create --name <o> --company <c> --amount <a> --stage Qualification|Proposal|Screening|Won|Lost`
  - `task create --title <t> --due <date> --link <opp-id>`
  - `note create --body <text> --link <person|company|opp>`
- **后端**：开源 EspoCRM/SuiteCRM REST API wrapper，或 sqlite-backed mini-CRM

### 10. `cli-anything-hrms-shim` 或 `cli-anything-orangehrm`（HR）

- **路径**：`hrms/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=hrms/agent-harness`
- **entry_point**：`cli-anything-hrms`
- **核心命令**：
  - `employee create/set --id HR-EMP-NNNNN --name <n> --dept <d> --joining <date>`
  - `leave allocate --employee <id> --type <t> --days <n>`
  - `salary structure set --employee <id> --base <a> --components <json>`
  - `appraisal cycle create / goal set / kra add`
  - `recruitment opening create / applicant add / interview schedule`
  - `report run --kind attendance|salary-register|income-tax|leave-balance`
- **后端**：包装开源 OrangeHRM/Frappe HRMS REST API

### 11. `cli-anything-pretix-shim`（活动售票）

- **路径**：`pretix/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=pretix/agent-harness`
- **entry_point**：`cli-anything-pretix`
- **核心命令**：
  - `event create --slug <s> --name <n> --currency <c> --organizer <o>`
  - `product create --event <e> --name <p> --price <p> --quota <q>`
  - `voucher create --event <e> --code <c> --discount-pct <p> --products <ids> --max-usages <n>`
  - `quota create --event <e> --name <q> --size <n> --products <ids>`（shared quota）
  - `checkin-list create --event <e> --name <l> --products <ids>`
  - `tax-rule set --event <e> --rate <r>`
- **后端**：直接包 pretix REST API；自托管 Pretix 才能 verify

### 12. `cli-anything-openemr-shim` 或 `cli-anything-emr`（电子病历）

- **路径**：`openemr/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=openemr/agent-harness`
- **entry_point**：`cli-anything-openemr`
- **核心命令**：
  - `patient create/set --id <id> --name <n> --dob <date>`
  - `encounter create --patient <p> --date <d> --provider <pr>`
  - `vitals record --encounter <e> --bp <bp> --hr <hr> --spo2 <p>`
  - `fee-sheet add --encounter <e> --icd10 <c> --cpt <c> --price <p>`
  - `immunization record --patient <p> --vaccine <v> --lot <l> --route <r>`
  - `merge patients --primary <id> --duplicate <id>`
  - `disclosure log --patient <p> --recipient <r> --purpose <text>`
- **后端**：sqlite + FHIR R4 风格 schema

### 13. `cli-anything-mattermost-shim`（IM 自托管）

- **路径**：`mattermost/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=mattermost/agent-harness`
- **entry_point**：`cli-anything-mattermost`
- **核心命令**：
  - `team create / channel create / channel add-user`
  - `post send --channel <c> --text <t> --attach <file>`
  - `post search --channel <c> --query <q>`
  - `webhook create --channel <c> --url <u>`
- **后端**：直接 Mattermost REST API

### 14. `cli-anything-owncloud-shim`（网盘）

- **路径**：`owncloud/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=owncloud/agent-harness`
- **entry_point**：`cli-anything-owncloud`
- **核心命令**：
  - `file upload --src <local> --dst <remote>`
  - `file share --path <p> --user <u> --permission read|write`
  - `folder create --path <p>`
  - `link create --path <p> --expires <date> --password <pw>`
- **后端**：包装 WebDAV PROPFIND/PUT + OCS API（很轻量）

### 15. `cli-anything-roundcube-shim` 或 `cli-anything-imap`（邮箱接收）

- **路径**：`imap/agent-harness/`
- **install_cmd**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=imap/agent-harness`
- **entry_point**：`cli-anything-imap`
- **核心命令**：
  - `mailbox list / message search --query <q>`
  - `message read --uid <id>`
  - `message send --to <addr> --subject <s> --body <text> --attach <file>`
  - `message move --uid <id> --folder <f>`
  - `message flag --uid <id> --read|--unread|--star`
- **后端**：imapclient + smtplib（轻包装）

## Software 类的特殊问题：baserow / metabase verify

Software 类 31 个任务大量依赖 baserow 的强类型 schema（single-select、number、date、link field）、views（Grid/Kanban/Form）、和 metabase 的 saved-question + dashboard。chromadb metadata 只能存 key-value 字符串/数字，**无原生 join、view、form**。这会让 verify.py 即使改为读 chromadb 也无法判断"single-select 是否正确"、"Kanban 是否 stacked by Status"。**软件类是替代最弱、verify 重写代价最高的类别。**最关键的缺口是 #7 `cli-anything-baserow-shim`，建议优先实现。

## verify.py 风险（已知未解决）

- 原 verify.py 通过 `docker exec` 进入 SaaS 容器查 DB 或调 HTTP API 校验任务结果。
- CLI 替代后容器不再启动，verify.py 全部会因 `Container not found` 或 `connection refused` 失败。
- **需要做的**（本次未做）：
  1. 改 verify.py：读 obsidian vault 文件存在性 + frontmatter 字段、calibre `calibredb list --search` 命中、chromadb HTTP `/api/v2/collections/<c>/get` 查询结果、seaclip `seaclip-cli issue list` 输出、stata `.do` 脚本+`.gph` 文件存在、libreoffice 转换后 PDF/XLSX 文件结构。
  2. 改 `saas_bench/apps.yaml`：为新 CLI 增加"非 docker app"占位条目（或在 loader 里放宽 `Unknown app keys are ignored with a warning`，让 verify.py 直接读 env var 找 CLI 服务地址）。
  3. 改 `saas_bench/run.py` / `slot.py`：跳过 docker 启动，改为 `pre_task_cmd` 准备 vault/chromadb namespace/seaclip 工作目录。

## 备份还原

```bash
cd /Users/luwei/work/Controversy/chat/SaaS-Bench/tasks
for d in $(find . -name description.saas.md -exec dirname {} \;); do
  cp "$d/description.saas.md" "$d/description.md"
  cp "$d/meta.saas.json" "$d/meta.json"
done
```

## 文件清单

```
tasks/multi-m/Agriculture/agriculture_{003,007,011,012,013,016,020,021,022,031,038,042}/ (12)
tasks/multi-m/Media/media_{006,011,012,016,020,024,027,029,033,035,060,063,065,066,067,068,069,070,072,073}/ (20)
tasks/uni-m/Business/business_{023,031,032,051,052,062,065,084,110,121,135,143,144,155,302}/ (15)
tasks/uni-m/Healthcare/healthcare_{001,002,007,013,015,017,019,021,023,025,026,030,034,038,045,048}/ (16)
tasks/uni-m/Software/software_{002,004,005,006,008,009,012,014,018,021,023,024,025,026,027,029,030,031,032,033,034,035,038,039,040,041,042,043,044,046,047}/ (31)
tasks/uni-m/Teamwork/teamwork_{009,011,014,020,030,032,042,043,052,074,082,083}/ (12)
```

每个目录现含 `description.md`（CLI 版）+ `description.saas.md`（备份）+ `meta.json`（CLI 版）+ `meta.saas.json`（备份）+ `verify.py`（未动）。
