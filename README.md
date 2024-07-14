# personal-website 个人网站

##### public：存放的是生成的页面
##### scaffolds：命令生成文章等的模板
##### source：用命令创建的各种文章
##### themes：主题
##### _config.yml：整个博客的配置
##### db.json：source解析所得到的
##### package.json：项目所需模块项目的配置信息

---
## hexo
官网：[Hexo](https://hexo.io/zh-cn/)
### 推荐主题
- maupassant: https://github.com/tufu9441/maupassant-hexo
- book: https://github.com/kaiiiz/hexo-theme-book
- Kratos-Rebirth: https://github.com/Candinya/Kratos-Rebirth
- 3-hexo: https://github.com/yelog/hexo-theme-3-hexo
- butterfly: https://github.com/jerryc127/hexo-theme-butterfly
---

## 常用命令
```javascript
//项目检查：以下命令分别执行即可
npm install -g npm-check     //安装npm-check
npm-check               //查看系统插件是否需要升级

npm install -g npm-upgrade   //安装npm-upgrade
//在执行npm-upgrade命令后会要求输入yes或者no，直接输入Yes或Y即可
npm-upgrade        //更新package.json
npm update -g      //更新全局插件
npm update --save  //更新系统插件
```

### 插件
```javascript
// hexo-admin 博客管理工具
npm install --save hexo-admin
hexo server -d
open "http://localhost:4000/admin/"

// 发布插件：
npm install hexo-deployer-git --save
// deploy:
//     type: git
//     repo: git@github.com:yemenghexo/yemenghexo.github.io.git
//     branch: gh-pages


```