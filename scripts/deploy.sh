#!/bin/bash

# OpenSource Copilot 部署脚本
# 使用方法: ./scripts/deploy.sh [frontend|backend|all]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 部署前端到 Vercel
deploy_frontend() {
    log_info "开始部署前端到 Vercel..."
    
    cd frontend
    
    # 检查是否安装了 Vercel CLI
    if ! command -v vercel &> /dev/null; then
        log_warn "Vercel CLI 未安装，正在安装..."
        npm i -g vercel
    fi
    
    # 构建
    log_info "构建前端..."
    npm run build
    
    # 部署
    log_info "部署到 Vercel..."
    vercel --prod
    
    cd ..
    
    log_info "前端部署完成！"
}

# 部署后端到 Railway
deploy_backend() {
    log_info "开始部署后端到 Railway..."
    
    cd backend
    
    # 检查是否安装了 Railway CLI
    if ! command -v railway &> /dev/null; then
        log_warn "Railway CLI 未安装，请先安装: npm i -g @railway/cli"
        log_info "或访问 https://railway.app 手动部署"
        return 1
    fi
    
    # 部署
    log_info "部署到 Railway..."
    railway up
    
    cd ..
    
    log_info "后端部署完成！"
}

# 显示帮助
show_help() {
    echo "OpenSource Copilot 部署脚本"
    echo ""
    echo "使用方法:"
    echo "  ./scripts/deploy.sh frontend    # 部署前端到 Vercel"
    echo "  ./scripts/deploy.sh backend     # 部署后端到 Railway"
    echo "  ./scripts/deploy.sh all         # 部署全部"
    echo ""
    echo "前置要求:"
    echo "  1. 安装 Node.js 和 npm"
    echo "  2. 安装 Vercel CLI: npm i -g vercel"
    echo "  3. 安装 Railway CLI: npm i -g @railway/cli"
    echo "  4. 登录 Vercel: vercel login"
    echo "  5. 登录 Railway: railway login"
}

# 主逻辑
case "$1" in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    all)
        deploy_backend
        deploy_frontend
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac

