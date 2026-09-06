// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "nav-publications",
          title: "publications",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "A small selection of research systems and side projects.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "post-agentic-rl-综述-工具调用-信用分配与训练稳定性-从-rap-到-aepo",
        
          title: "Agentic RL 综述：工具调用、信用分配与训练稳定性——从 RAP 到 AEPO",
        
        description: "梳理 Agentic RL 从树搜索到可训练策略的演进，涵盖 Planner-R1、TORL/ToolRL/ARTIST、GiGPO/ARPO、RAGEN/RAGEN-2 及 AEPO，聚焦 reward 设计、credit assignment 与 reasoning collapse 三大核心问题。",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/agentic-rl/";
          
        },
      },{id: "post-opd-如何重构后训练的不可能三角",
        
          title: "OPD 如何重构后训练的不可能三角",
        
        description: "后训练希望学习信号同时准确、稠密、易得，但现实里很难三者兼得。OPD 提供了一种新的组织方式——在学生自己的轨迹上，把教师、验证器、环境反馈组织成密集监督。",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/opd-deep-dive/";
          
        },
      },{id: "post-training-free-prompt-optimization-从经验库到问题重构",
        
          title: "Training-Free Prompt Optimization：从经验库到问题重构",
        
        description: "关于 training-free prompt optimization、GRPO、经验库与 3DrawAgent 的一些思考",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/training-free-prompt-optimization/";
          
        },
      },{id: "post-远程连接服务器时的-ai-编程工具实践与配置指南",
        
          title: "远程连接服务器时的 AI 编程工具实践与配置指南",
        
        description: "探讨在远程连接服务器时使用 Cursor、Copilot、Claude Code 等 AI 工具的优缺点及网络转发配置方案",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/cli-in-ssh/";
          
        },
      },{id: "post-task-vector-in-multimodal-in-context-learning-论文阅读笔记",
        
          title: "Task Vector in Multimodal In-Context Learning 论文阅读笔记",
        
        description: "Notes on task vectors, function vectors, in-context vectors, and multimodal in-context learning.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/task-vector-multimodal-icl/";
          
        },
      },{id: "post-leetcode学习笔记",
        
          title: "Leetcode学习笔记",
        
        description: "Notes on Leetcode",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/leetcode-notes/";
          
        },
      },{id: "post-self-distillation论文阅读",
        
          title: "Self-Distillation论文阅读",
        
        description: "Notes on Papers about Self Distillation",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/self-distillation/";
          
        },
      },{id: "post-llm八股学习与手撕",
        
          title: "LLM八股学习与手撕",
        
        description: "Notes on LLM algorithms",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/algorithm-notes/";
          
        },
      },{id: "post-claude-code-配置与-cc-switch-代理接入完全指南",
        
          title: "Claude Code 配置与 CC Switch 代理接入完全指南",
        
        description: "从零配置 Claude Code 走第三方 API，含 CC Switch 本地代理、CLI 与 VS Code 插件统一接入、排查命令和迁移清单",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/cc-config/";
          
        },
      },{id: "post-aaai2026参会记录",
        
          title: "AAAI2026参会记录",
        
        description: "Log of experience in AAAI2026",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/aaai-log/";
          
        },
      },{id: "post-lora-for-continual-learning-论文阅读笔记",
        
          title: "LoRA for Continual Learning 论文阅读笔记",
        
        description: "Notes on LoRA-based continual learning methods, including InfLoRA, BiLoRA, TreeLoRA, CLoRA, and AnySSR.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2025/lora4cl/";
          
        },
      },{id: "post-编程错误",
        
          title: "编程错误",
        
        description: "Log of bug in coding",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2024/codeexp/";
          
        },
      },{id: "post-bupt-ai大三下生存指南",
        
          title: "BUPT AI大三下生存指南",
        
        description: "Life of the spring semester of junior year in BUPT AI",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2024/formatting-and-links/";
          
        },
      },{id: "news-awarded-funding-from-the-quot-qiyan-quot-program",
          title: 'Awarded funding from the &amp;quot;Qiyan&amp;quot; Program',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/20240905/";
            },},{id: "news-one-paper-accepted-by-aaai-2026",
          title: 'One paper accepted by AAAI 2026! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-by-advanced-engineering-informatics",
          title: 'One paper accepted by Advanced Engineering Informatics! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "news-started-internship-at-bytedance-data",
          title: 'Started internship at ByteDance Data',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/20260610/";
            },},{id: "news-one-paper-accepted-by-emnlp-2026-arxiv-preprint-and-code-will-be-released-soon",
          title: 'One paper accepted by EMNLP 2026! 🎉🎉🎉 ArXiv preprint and code will be...',
          description: "",
          section: "News",},{id: "projects-arxiv-digest",
          title: 'arXiv-Digest',
          description: "面向个人研究者的论文阅读自动化流水线：定时抓取 arXiv 关键词新论文，结合 MinerU 全文解析与 LLM 多维打分，推送结构化决策卡至飞书。",
          section: "Projects",handler: () => {
              window.location.href = "/projects/arxiv-digest/";
            },},{id: "projects-knots",
          title: 'Knots',
          description: "面向航空航行通告（NOTAM）的大规模多智能体增强专家标注数据集与语义解析Prompt优化基准。",
          section: "Projects",handler: () => {
              window.location.href = "/projects/knots/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%6C%69%75%6D%61%6F%71%69@%62%75%70%74.%65%64%75.%63%6E", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/Estrellajer", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
