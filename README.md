# mySkills

個人使用的 agent skills 與工具收藏。

## 目錄

```text
skills/
├── commit/          # Git 提交流程
├── cp-master/       # 高 CP 值選項調查
├── how/             # 解釋程式碼架構與運作流程（源自 cursor/plugins pstack）
├── latex-slides/    # LaTeX 簡報製作
├── recall/          # 從 git 與 Claude Code／Codex／Pi 對話紀錄產出專案近況簡報（改寫自 cursor/plugins pstack）
├── slim/            # 把 Claude Code 的內建 skill 與工具關成白名單
├── spec-foreman/    # 規格導向的多 agent TDD 與 review 流程
└── unslop/          # 去除文字中的 AI 腔（源自 cursor/plugins pstack）

tools/
├── PiStatusLine/    # Pi status line 工具與安裝說明（舊版，無 tok/s）
└── statusline/      # Claude Code 與 Pi 目前使用的 statusline，以及 Pi 插件清單

packages/
├── latex-slides.skill
└── PiStatusLine.zip
```

- `skills/`：各 skill 的原始內容，每個資料夾以 `SKILL.md` 為入口。
- `tools/`：解壓後的工具；PiStatusLine 的使用方式請參閱 [README](tools/PiStatusLine/README.md)。
- `tools/statusline/`：Claude Code 與 Pi statusline 的還原步驟請參閱 [README](tools/statusline/README.md)，Pi 插件的作者、來源與安裝指令列在 [EXTENSIONS.md](tools/statusline/EXTENSIONS.md)。
- `packages/`：保留原始壓縮包，方便分發與還原；不保證與解壓後修改的內容同步。

PiStatusLine 壓縮包內附的另一份 `PiStatusLine.zip` 也保留在工具目錄中，未修改原始內容。
