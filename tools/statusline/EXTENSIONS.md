# 目前使用的 pi extensions

此檔僅記錄作者、來源及安裝指令，**不打包第三方 extension 原始碼或 node_modules**。

| 名稱 | 作者／來源維護者 | 目前版本 | 安裝指令 |
| --- | --- | --- | --- |
| [pi-statusline](https://github.com/hsingjui/pi-statusline) | hsingjui | 0.0.2 | `pi install npm:pi-statusline` |
| [pi-askuserquestion](https://github.com/ghoseb/pi-askuserquestion) | ghoseb | Git 套件 | `pi install git:github.com/ghoseb/pi-askuserquestion` |
| [i-have-adhd](https://github.com/ayghri/i-have-adhd) | ayghri | 0.4.1 | `pi install https://github.com/ayghri/i-have-adhd` |
| [pi-notify](https://github.com/ferologics/pi-notify) | ferologics | 1.4.0 | `pi install npm:pi-notify` |
| [pi-subagents](https://github.com/tintinweb/pi-subagents) | tintinweb | 0.22.0 | `pi install npm:@tintinweb/pi-subagents` |
| [pi-btw](https://github.com/dbachelder/pi-btw) | Dan Bachelder / dbachelder | 0.8.0 | `pi install npm:pi-btw` |

上述指令安裝來源當前版本。如需相同 npm 版本，可在套件名稱後加上 `@版本`，例如 `pi install npm:pi-statusline@0.0.2`。

原機 Git commit（供重現版本參考）：
- pi-askuserquestion：`e58609c9e9c8c4e8a0348c96eaad38dd7e6f0578`
- i-have-adhd：`1ecea1993b7fce257ffbd686c070948b5e07eda6`

## 原機另有本機整合

- `herdr-agent-state.ts`：由 Herdr 安裝、管理的 pi 整合。未打包；有需要時從 Herdr 重新啟用 pi 整合。
- `tokps`：本機自訂的 statusline tok/s 統計模組，無獨立下載來源。這是 pi statusline 的必要相依，因此只保留其 `index.ts` 與 `stats.mjs`，不是第三方插件備份。
