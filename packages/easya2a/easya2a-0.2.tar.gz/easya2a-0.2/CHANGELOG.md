# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-14

### Added
- 🎯 **全新三步式API设计** - 革命性的用户体验
  - `A2AAgentWrapper.set_up()` - 初始化方法
  - 链式配置方法 - 流畅的配置体验
  - `run_a2a()` - 一键启动服务
- 🔧 **智能Agent适配器** - 自动检测Agent类型
  - LangChain Agent支持
  - OpenAI Assistant支持
  - 自定义Agent支持
- 📡 **完整A2A协议集成** - 标准化协议支持
  - 自动Agent Card生成
  - 标准端点实现
  - 协议兼容性保证
- ⚡ **性能优化** - 生产级性能
  - 异步处理支持
  - 延迟初始化
  - 连接池管理
- 📊 **监控与调试** - 完善的可观测性
  - 详细启动信息
  - 结构化日志
  - 健康检查端点
- 🚀 **部署支持** - 多环境部署
  - Docker支持
  - 环境变量配置
  - 生产环境优化

### Changed
- 💥 **BREAKING**: 重构API设计，不向后兼容
- 📦 **包结构优化** - 更清晰的模块组织
- 📚 **文档重写** - 全新的文档体系

### Improved
- 🎨 **用户体验** - 代码量减少70%
- 🔍 **错误处理** - 更友好的错误信息
- 🛡️ **类型安全** - 完整的类型注解

### Technical Details
- Python 3.8+ 支持
- 基于 Starlette/FastAPI
- 完整的异步支持
- 生产级错误处理

## [1.0.0] - 2024-12-01

### Added
- 初始版本发布
- 基础A2A包装功能
- LangChain Agent支持
- 基本配置系统

### Features
- Agent包装器
- 配置管理
- Web服务器
- 基础文档

---

## 版本说明

### 版本号规则
- **主版本号**: 不兼容的API修改
- **次版本号**: 向后兼容的功能性新增
- **修订号**: 向后兼容的问题修正

### 发布周期
- **主版本**: 根据需要发布
- **次版本**: 每月发布
- **修订版**: 根据需要发布

### 支持政策
- **当前版本**: 完整支持
- **前一个主版本**: 安全更新
- **更早版本**: 不再支持
