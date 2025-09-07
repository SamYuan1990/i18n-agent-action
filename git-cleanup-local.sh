#!/bin/bash

# 获取默认分支名称（优先检查 main，然后 master）
DEFAULT_BRANCH=$(git remote show origin | grep "HEAD branch" | cut -d" " -f5)

# 如果没有设置远程，尝试本地检测
if [ -z "$DEFAULT_BRANCH" ]; then
    if git show-ref --verify --quiet refs/heads/main; then
        DEFAULT_BRANCH="main"
    elif git show-ref --verify --quiet refs/heads/master; then
        DEFAULT_BRANCH="master"
    else
        echo "错误: 无法确定默认分支"
        exit 1
    fi
fi

echo "默认分支: $DEFAULT_BRANCH"

# 切换到默认分支
git checkout $DEFAULT_BRANCH
git pull origin $DEFAULT_BRANCH

# 获取所有本地分支列表（排除当前分支/默认分支）
BRANCHES=$(git branch | grep -v "$DEFAULT_BRANCH")

if [ -z "$BRANCHES" ]; then
    echo "没有需要清理的分支"
    exit 0
fi

echo "以下分支将被删除:"
echo "$BRANCHES"

# 确认操作
read -p "确定要删除这些分支吗? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

# 删除分支
echo "$BRANCHES" | xargs git branch -D

echo "分支清理完成"