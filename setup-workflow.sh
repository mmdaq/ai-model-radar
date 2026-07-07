#!/bin/bash
# 将 workflow 文件移到正确位置
mkdir -p .github/workflows
mv .github/workflow-file.yml .github/workflows/daily-email.yml
git add .github/workflows/daily-email.yml
git rm .github/workflow-file.yml
git commit -m "chore: move workflow to correct path"
git push
echo "✅ Workflow 设置完成！"
