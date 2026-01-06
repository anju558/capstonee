import * as vscode from "vscode";
import { sendToBackend } from "./api";

export function registerEvents(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(() => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      const diagnostics = vscode.languages
        .getDiagnostics(editor.document.uri)
        .map(d => ({
          message: d.message,
          line: d.range.start.line + 1
        }));

      sendToBackend({
        language: editor.document.languageId,
        code: editor.document.getText(),
        diagnostics
      });
    })
  );
}
