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
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-repositories",
          title: "repositories",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/repositories/";
          },
        },{id: "nav-cv",
          title: "cv",
          description: "Not prepared yet.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "post-远程连接服务器时的-ai-编程工具实践与配置指南",
        
          title: "远程连接服务器时的 AI 编程工具实践与配置指南",
        
        description: "探讨在远程连接服务器时使用 Cursor、Copilot、Claude Code 等 AI 工具的优缺点及网络转发配置方案",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/cli-in-ssh/";
          
        },
      },{id: "post-ai-驱动的未来-焦虑频发下的深度思考",
        
          title: "AI 驱动的未来：焦虑频发下的深度思考",
        
        description: "在疾病缠绕与工作重压的间隙，关于 AI 冲击下职业前景与人际关系的感悟",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/thoughts-of-future/";
          
        },
      },{id: "post-第一次面试总结复盘",
        
          title: "第一次面试总结复盘",
        
        description: "第一次面试复盘：技术面与HR面",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/interview-summary/";
          
        },
      },{id: "post-leetcode学习笔记",
        
          title: "Leetcode学习笔记",
        
        description: "Notes on Leetcode",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/leetcode-notes/";
          
        },
      },{id: "post-当我们谈论焦虑",
        
          title: "当我们谈论焦虑",
        
        description: "When we talk about anxiety",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/on-anxiety/";
          
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
      },{id: "post-claude-code配置",
        
          title: "Claude Code配置",
        
        description: "How to use Claude Code in restricted area",
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
      },{id: "news-awarded-funding-from-the-quot-qiyan-program-quot",
          title: 'Awarded funding from the &amp;quot;Qiyan” Program&amp;quot;',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/20240905/";
            },},{id: "news-one-paper-accepted-by-aaai2026-ccf-a",
          title: 'One Paper accepted by AAAI2026(CCF-A)! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-by-advanced-engineering-informatics-ccf-b-sci-q1",
          title: 'One Paper accepted by Advanced Engineering Informatics(CCF-B, SCI-Q1)! 🎉🎉🎉',
          description: "",
          section: "News",},{id: "projects-project-1",
          title: 'project 1',
          description: "with background image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{id: "projects-project-2",
          title: 'project 2',
          description: "a project with a background image and giscus comments",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_project/";
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
