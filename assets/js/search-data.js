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
            },},{id: "news-one-paper-accepted-by-aaai2026-ccf-a",
          title: 'One Paper accepted by AAAI2026(CCF-A)! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-by-advanced-engineering-informatics-ccf-b-sci-q1",
          title: 'One Paper accepted by Advanced Engineering Informatics(CCF-B, SCI-Q1)! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "news-started-internship-at-bytedance-data",
          title: 'Started internship at ByteDance Data',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/20260610/";
            },},{id: "projects-knots",
          title: 'Knots',
          description: "A large-scale expert-annotated dataset and prompt optimization pipeline for NOTAM semantic parsing.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/knots/";
            },},{id: "projects-notam-evolve",
          title: 'NOTAM-Evolve',
          description: "A knowledge-guided self-evolving framework with LLMs for NOTAM interpretation.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/notam-evolve/";
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
        id: 'social-custom_social',
        title: 'Custom_social',
        section: 'Socials',
        handler: () => {
          window.open("https://www.alberteinstein.com/", "_blank");
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
