import * as vscode from "vscode";
import { SkillAgentPanel } from "./panel";
import { registerEvents } from "./events";

export let panel: SkillAgentPanel;

export function activate(context: vscode.ExtensionContext) {
  panel = new SkillAgentPanel();

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      SkillAgentPanel.viewType,
      panel
    )
  );

  // 🔥 FORCE OPEN THE PANEL
  vscode.commands.executeCommand(
    "workbench.view.extension.skillCoachContainer"
  );

  registerEvents(context);
}
