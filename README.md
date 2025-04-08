# Thinking in MCP

[![Documentation Status](https://readthedocs.org/projects/thinking-in-mcp/badge/?version=latest)](https://thinking-in-mcp.readthedocs.io/en/latest/?badge=latest)

## 目录

1. [项目简介](#1-项目简介)
2. [项目结构](#2-项目结构)
3. [依赖要求](#3-依赖要求)
4. [构建文档](#4-构建文档)
   4.1. [方式一：使用 make 命令](#41-方式一使用-make-命令)
   4.2. [方式二：使用 sphinx-autobuild（推荐）](#42-方式二使用-sphinx-autobuild推荐)
5. [在线文档](#5-在线文档)
6. [许可证](#6-许可证)
7. [贡献指南](#7-贡献指南)
8. [联系方式](#8-联系方式)

## 1. 项目简介

Thinking in MCP 是一个使用 Sphinx 构建的文档项目，旨在提供关于 MCP（Model Context Protocol）的深入思考和最佳实践。

## 2. 项目结构

```
.
├── source/              # 文档源代码
│   ├── docs/           # 文档内容
│   ├── _static/        # 静态资源
│   ├── _templates/     # 模板文件
│   ├── conf.py         # Sphinx 配置文件
│   └── index.rst       # 文档首页
├── Makefile            # 构建脚本
├── make.bat            # Windows 构建脚本
├── requirements.txt    # 项目依赖
└── .readthedocs.yaml   # Read the Docs 配置文件
```

## 3. 依赖要求

- recommonmark
- sphinx_markdown_tables
- sphinxcontrib.video
- sphinx_rtd_theme
- sphinx
- rst2pdf
- sphinx-autobuild

## 4. 构建文档

### 4.1. 方式一：使用 make 命令

#### Linux/macOS

```bash
make html
```

#### Windows

```bash
make.bat html
```

### 4.2. 方式二：使用 sphinx-autobuild（推荐）

使用 sphinx-autobuild 可以实时预览文档更改：

```bash
sphinx-autobuild source build/html
```

这将启动一个本地服务器，默认地址为 http://127.0.0.1:8000。当你修改文档时，页面会自动刷新。

## 5. 在线文档

项目文档托管在 Read the Docs 上，可以通过以下链接访问：

https://thinking-in-mcp.readthedocs.io/

## 6. 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 7. 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交之前，请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试
3. 更新相关文档

## 8. 联系方式

如有任何问题或建议，请通过 Issue 与我们联系。