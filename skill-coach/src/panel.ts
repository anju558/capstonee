import * as vscode from "vscode";

export class SkillAgentPanel implements vscode.WebviewViewProvider {
  public static readonly viewType = "skillCoach.panel";
  private view?: vscode.WebviewView;

  resolveWebviewView(view: vscode.WebviewView) {
    this.view = view;

    view.webview.options = { enableScripts: true };
    view.webview.html = this.getHtml();
  }

  update(data: any) {
    if (!this.view) return;

    this.view.webview.postMessage({
      type: "update",
      payload: data
    });
  }

  private getHtml(): string {
    return `
      <!DOCTYPE html>
      <html>
      <body>
        <h3>🧠 Skill Coach</h3>
        <div id="content">Waiting for errors...</div>

        <script>
          window.addEventListener("message", event => {
            const { type, payload } = event.data;
            if (type === "update") {
              document.getElementById("content").innerHTML =
                "<pre>" + JSON.stringify(payload, null, 2) + "</pre>";
            }
          });
        </script>
      </body>
      </html>
    `;
  }
}
