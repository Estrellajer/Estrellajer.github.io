---
layout: post
title: "EMNLP 2026: Do as Agent Do"
date: 2026-11-08 20:00:00
description: 记 EMNLP 2026 布达佩斯参会与迪拜、维也纳一周之行：在陌生的风景与交流中获得新的 Context，重新感受“钉子”的痛感，起身行动。
tags: emnlp travel reflection
categories: Life
---

## 前言

本来想着这篇内容能更新得快一点，但事实证明，远离各种事情一周之后，回来迎面而来的就是干不完的活。还是不得不在周末抽空写一下，要不然拖到后面记忆慢慢褪色，很多当时鲜活的感受也会变得陌生，难以回忆。以前的我总觉得鲜活的记忆永远不会褪色，但时间长了其实都会被冲刷掉，所以现在习惯性地穿插记录——当然，也可能确实不算年轻了，正在向着“中登”迈进。

小时候忘了在哪里看到过一个故事，叫“狗躺钉子”。这个故事通篇的妙处就在于一个“躺”字。钉子是扎人的，肯定会让你觉得疼；但“躺”着，说明你就像温水煮青蛙一样，刚开始觉得疼，后面习惯了也不觉得有什么，变得麻木迟钝。直到某些事情又让你重新敏感起来，再次感受到钉子扎在身上的痛感，你才会选择站起来，而不是继续躺在上面。

对我来说也是一样。感觉自己在钉子上躺太久了，平时的生活基本两点一线，有了惯性，很难有什么深入思考和实践。这次参会兼旅游，算是让我跳出来重新想了想之前反反复复纠结的问题，一路上也碰到了很多有意思、很 nice 的人。Anyway，我现在确实重新变得敏感，要从钉子上挣扎着爬起来了。做决定之前固然会犹豫，但一旦做了决定，就要坚定地去执行。

至于题目为什么叫 `Do as Agent Do`，因为现代 Agent 的典型架构还是 ReAct：先 Obtain 一些 Context，进行一些 Reasoning，最后执行 Action。和人一生的探索也挺像的，不是吗？

## 0. 出发之前

其实投稿前发现今年 EMNLP 在布达佩斯开，我就在想有没有机会去。毕竟大部分人应该都在网上刷到过夜晚在多瑙河畔举着香槟庆祝的短视频，或者听过知名的《布达佩斯大饭店》（虽然这电影根本不是在布达佩斯取的景）。但等论文真中了，脑子里又会冒出各种杂七杂八的顾虑，没动力起身。这时候其实很简单，就像高中看《孤独星球》里说的，只要出发，就已经解决了旅行中 90% 的困难。让身体先动起来去准备签证材料，顺着惯性推着自己往前走就好了。虽然出发前一天还在实验室挂着实验，但总归是收拾好东西踏上了行程。

参加这次 EMNLP 的目的很简单：一个是很久没出去了，想散散心；第二是看去年赞助商很多，希望来找找机会；第三是 EMNLP 相对来说还是个声誉不错的会，希望能认识些人，获取一点 Context。毕竟现在这个时代，Connection 大于一切。

## 0.5 10.24 迪拜 🥵

因为在迪拜转机有 22 个小时，索性订了酒店住一晚，当作前置行程。

迪拜给我的第一印象就是热，走出机舱踏上廊桥就能感受到扑面而来的热浪；第二感受是外劳和白人美女非常多，这大概也是它发达和国际化程度的一种体现；第三就是很多小细节能看出土豪国家的实力，比如海关落地直接白送一张 10G 的流量卡，还有各种基建。

落地后和在小红书上找的搭子琛博汇合，一起沿着 Creek 逛了博物馆和网红街区。博物馆非常有设计感，里面很多互动装置在国内没见过，挺新奇的。虽然外观看着并不宏伟，但内里别有洞天，让人感觉这个国家并不是纯粹的暴发户，至少博物馆修得很用心。街区里非常多本地人会说中文，一路冲你喊“朋友”、“帅哥”，应该都是为了招揽游客。不知道是不是去的时间不凑巧，街上感觉没什么人。那个号称“最美星巴克”的地方傍晚看着也很一般，随便拍张照就走了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/TAb4bivN6o31raxMGJncgtvjnOd.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="Creek" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/IWyGbUt0coFXX8xSVZacMy3vnim.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="博物馆的一间房" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/I4RpbF8q6oqUT1xlkYscnA5pn1B.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="街区" %}
  </div>
</div>

晚上坐地铁去 Dubai Mall。迪拜的地铁覆盖面还挺广的，但从地铁站通往商场的室内廊桥长到夸张，走了半天才真正进到商场里。商场里有一家规模极其庞大的书店，国内商场虽然也会给书店补贴租金，但通常见不到这么讲排场、这么豪奢的书店。晚饭去吃了成龙也去吃过的牛尾饭，消费算比较高的，服务员甚至会用中文问你“辣不辣”，最后还是给了 10% 的小费。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/I00vbxW8bocLguxnCF5c29lVnmf.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="牛尾饭，味道中规中矩的好吃" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/NQDMbujwzooXr3xxl2pc1rCsnJp.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="哈利法塔" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/GBhXbK5phoLlajxCCcNcch2ennb.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="迪拜Mall外景" %}
  </div>
</div>

吃完饭往回走，在河畔看哈利法塔和音乐喷泉。晚上的河边没有白天那么燥热，吹着微风，看着曾经的世界第一高楼，周围开放式酒馆里到处是端着酒杯的俊男靓女，确实能感受到一种纸醉金迷的味道。在这里，你完全感受不到经济下行，也察觉不到中东局势的动荡。

顺带一提，我和琛博可能观察得都比较粗糙，同程的女生就发现商场里大多是穿着传统服饰的男性结伴逛街购物，还挺奇妙的。

## 1. 10.25 布达佩斯 🥶

早上赶飞机飞布达佩斯。落地过海关的队伍排得极其慢，前面恰好赶上台湾来的旅行团，周围还夹杂着各路形形色色的奇怪路人，硬生生排了一个多小时才出去。坐机场大巴和去酒店办入住时还出了点支付的小插曲——招行的 Visa 卡之前买交通票用美元额度就能刷，结果在酒店死活刷不过去，非得卡里有欧元才行，非常奇怪。

走出机场的第一感受就是整体旧旧的。秋风瑟瑟，呼啸而过的车辆加上满地落叶，空气清冷甚至有点肃杀，特别像深秋的北京郊区。先去会场注册、领完物资，转了一圈就到晚饭时间了。琛博拉我进了一个十几人的纯网友参会小群，大家决定晚上一起打车去找地方吃饭，顺便沿着多瑙河 City Walk。在 Taste Asian 附近兜兜转转发现稍微网红一点的店都在大排长队，最后挑了一家评分很高但没那么网红的本地餐厅。店里有吹拉弹唱的驻场，菜量巨大，我们四个人根本吃不完，人均折合人民币不到 200 块，就当地物价来说绝对算物美价廉了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/GF2lbyBMCo4iJRxeEA9cY6MWnbe.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="驻场乐队" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/QUQybzB85oFPGTxZc1acd4u6nZm.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="图片看着小，但是分量其实很大" %}
  </div>
</div>

吃饭的时候和同行的几个朋友聊天。其中有一位在日本理研待着的老博士，准备回国拿教职，在安全领域不说是不是 rising star，至少也算是个小山头了。他跟我们分享了很多不一样的经历，也聊了聊国内高校的现状，比如怎么设定方向、怎么带学生之类的。

在这边待着，最直观的感触就是当地人的松弛。他们天然就很外向，乐于跟人互动，不像国内大城市里有那么多“空心人”。匈牙利本身好像也没什么特别强势的支柱产业，甚至街上几乎看不到什么黑人和印度老哥（我跟同行的人开玩笑说，衡量一个国家发不发达，看外来务工的印度人比例是个很准的指标，这么看匈牙利确实不算发达），但这边的年轻人看着很有活力，完全没有那种消沉、死气沉沉的感觉。

晚点在会场门口碰到一个华人面孔的小哥，看样子也是来开会的，我本来想上去加个微信交流一下，聊起来才发现是台湾人。聊了些个人经历后让我颇为意外：原来在台湾，哪怕背景很不错的人，找的工作也很难做到真正的 Work-Life Balance，基本只有进外企才行；表面上年假挺多，实际上领导根本不批，当地劳动法在这方面居然也形同虚设。看来整个东亚或多或少都有一样的病灶，大家终究没法像匈牙利 local 一样活得那么松弛。这让我想到来的时候在飞机上看“街头小霸王”（高知版讲师）的最新视频。易大师活得是真的自洽，虽然看着疯疯癫癫，但至少我挺羡慕那种状态的——有自己坚持的东西，并且发自内心地相信自己最牛逼。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/I6lIbwX34odKIqxp0gVcv9vgnch.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="多瑙河" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/PvO1bvEc3ooHNRxfTRlcntZ7n8d.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="布达与佩斯" %}
  </div>
</div>

晚上顺着链子桥去拍照，方向还走反了。天上飘着小雨，河畔随处可见打卡的游客，甚至真有人带着香槟去拍。路过长椅时，看到有当地人就那么淋着雨、戴着耳机坐在上面安安静静地听歌。这种松弛感是国内那种刻意装出来的“假松弛”比不了的，因为他们是真的不 care 很多东西。白天会场里大家还在热火朝天地聊 RL、聊 Self-evolving、聊 RSI，但走出会场，这里的人根本不关心这些，他们可能只关心今天晚饭吃什么好。这种反差让人觉得挺割裂的。到了十点多，看天色太晚不太方便，就回青旅睡了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/YQpcbDRL2oxXaKxGfA9c1Qvunfb.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="夜景" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/A4r9btUPtokcpIxgT54cFzknnPh.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="这就是大概为什么叫“链桥”？" %}
  </div>
</div>

## 2. 10.26 会场 🔥

早上出门发现住处附近有个小超市，顺便解决了早餐并囤了瓶大水。店里没有任何英文标识，全靠盲猜，连结账也是全自助的。好在旁边有位热心的 local 小姐姐帮忙，不仅教我怎么结账，还帮我避雷了气泡水（把气泡水和普通矿泉水混着放的设计实在太反人类了）。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/BLXkb361YoFkDyxihePcUua3nDc.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="挂壁早餐" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/LyYab7SYfoclNnxwistcL8zVnJc.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="茶歇，拉完了" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/DCK2biauHolja9xS5mwcMjvCnse.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="晚宴，一般般" %}
  </div>
</div>

今天是主会第二天，去会场打野基本没什么收获，而且今年投的各个大厂晚宴又双叒叕“全聚德”了（虽然今年在欧洲开整体赞助都很少）😭

不过去各个公司的 Booth 找技术同学聊了聊，还是收获了不少新的 Context，这里就不展开了。

今年 EMNLP 的 Poster 环节气氛明显比 AAAI 好太多，绝大部分人都会老老实实站 Poster，互动也很热烈，把我都站累死了。逛和站 Poster 的时候也碰到了不少有意思的人：先是偶遇了 Co-author 的 Mentor，只可惜他们大本营在杭州；站自己 Poster 时，虽然我这篇的 Topic 偏传统 ML（Continual Learning），但居然有好些印度老哥和一位 MBZUAI 的印尼小哥专门找过来聊。印尼小哥特别热情，拉着我聊了半天，也算逼着我狠狠练了一把荒废已久的英语口语。另外，展板正反面刚好挨着一位东京大学的博士，问及为什么去日本读博，老哥非常真实地说主要还是因为喜欢二次元。据他所说，日本知名的课题组虽然老学究多，但对学生基本是放养状态——其实没有“负指导”就已经谢天谢地了，何况 Funding 还很充足。说来也挺感慨，国内大家现在全都一窝蜂扑在 LLM 上向钱看齐，反倒是国外一些不那么 FOMO 的地方还有人在坚持做试图寻找 insight 的 research。当然我还是简单的 LLM 信仰者🤭

另外看了一圈会场，发现纯 NLP 乃至围绕语言学做文章的工作依然非常多。可能这类工作在 NLP 会议上还是更容易中吧，就像 ACL 24 时有人调侃的那样：“我们 ACL 不是一个 AI Conference。”

聊了一圈下来，现在的求职体感非常残酷，基本就看三项：学历出身（很多 Research 的 Group 去了业界还是一个组），Pub 的数量和质量，实习经历；而且论文和实习还必须得高度对口。现在三者全占的人越来越多，哪怕一个岗位设再离谱的门槛，池子里都能筛出一大堆合格的 Candidate；要是只占其中两项，那更是多如牛毛。

正焦虑着，在会场又收到了导师催命一样的消息，让我抓紧处理手头另一篇论文的 Rebuttal。目前在投的两篇里，有一篇转投的分数还行，希望能顺利苟中；另一篇自己觉得做得还不错的工作反而拿了负分，只能认栽继续转投了。不过现在对这些也看淡了，多中一篇对我来说也没什么实质性的加成，毕竟都是之前攒下的垃圾 Topic。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Dp0IbqQrLoJuVoxt9vTcv5aenxh.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="蹦迪环节，视频不太好传，但是现场气氛非常热烈" %}
  </div>
</div>

## 3. 10.27 布达佩斯 🚶‍♀️

早上起来实在懒得去会场，干脆自己出去逛景点。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/GviSbKzXVodpNMxqfAocGfdbnlh.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/MmxVb4EIko0yRCxLrMRciAL7nfd.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/DGQtbzLwHoA4rrxXxM6cbprRnug.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/YHrebSbn9oGSCnx58JQcCVFInug.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

第一站去了渔人堡。早上去不收门票，建筑本身看着也就那样，没什么特别惊艳的；唯一的优点是占了个高点，往下俯瞰整个布达佩斯，因为城市里没有什么高大现代建筑遮挡，视野极其通透，确实有一览无余的辽阔感。顺着旁边的马加什教堂一路走到布达城堡，城堡本身也只是提供了一个高点，而且里面到处都在围起来修缮，搞得人心烦，看着乏善可陈。下山后顺便去了趟号称“世界最美麦当劳”的店，结果里面并没有卖传说中的鹅肝汉堡。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/SWV4b3CcVoEMSTx9mK1cByeKnHf.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/PEXmbIonzoS4UGxGf2QcoXbAnDR.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

中午为了吃顿心心念念的鹅肝，特意避开游客区，找了一家放眼望去全是本地人、大家都在叽里咕噜说匈牙利语的餐厅。本来想点招牌的鹅肝套餐，结果卖光了，服务员小哥就给我推荐了一道拿鹅肝当配菜的主菜。怎么说呢，作为一个平时很能吃牛胸口油的北方人，这顿正宗鹅肝还是把我腻得够呛，实在是太厚重了，感觉大部分国人应该都消受不起。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/FbpCbsqIlocHkqx30xdcSZiCnth.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="似乎是专业模特在拍摄商业广告" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Algxb66R3oDSXbxnqUBcT1Bdnhd.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="看着牛肉实则是鸭肉，谁能找到鹅肝🤭" %}
  </div>
</div>

下午赶回会场听了会儿颁奖典礼和 Closing Session。台上有个华人面孔的老师讲了半天，我盯了半天才认出来原来是李宏毅老师。会上还公布了明年 ARR 系列会议的举办地，没想到下一届 EMNLP 居然定在了墨西哥。墨西哥还是留给以后去探索吧，这么看明年必须得抓紧 ACL 的机会了，也是硕士毕业前唯二的投稿机会了。

傍晚想去自由桥（绿桥）打卡，紧赶慢赶去麦当劳买了个米其林联名的特制汉堡（折合人民币花了一百块，味道却非常一般）。结果五点半跑到桥上坐下时，天已经彻底黑透了，根本没有所谓的蓝调时刻。更要命的是天上飘着小雨，冷冽的河风呼呼地刮，坐在铁桥架子上冻得人实在遭不住，纯属失策。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/XkZtbygCYosmVzxjmE2c06MsnZf.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="修缮中" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Ry6nb85ZboYTP2xkvoPcVYbznzg.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="“偏我来时不逢春”" %}
  </div>
</div>

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/CQUbbsTDNo14sgxw0rgczVk4nVc.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/EYrXbK8rHomVLExDEpLciMkDnLf.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/W1z6b3XKaoQY0Xx84CqcSNZinqS.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

再晚一点去多瑙河岸边随便买了张船票坐游船。船舱里放眼望去基本都是来参会的中国人。网上那些短视频里在国会大厦前举着香槟碰杯看着极其 chill，但现实是十月底的布达佩斯气温跟北京深秋有一拼，加上河风，虽然我自认比较耐冻，但在甲板上待一会儿还是冻得半死。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/KHb6bOtwDowCl6xLqykcFfyyncd.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

因为实在太冷，很早就溜回青旅了。在公共区碰到一个韩国老哥，看着特别年轻有少年感，一聊才知道已经快 40 岁了。他 2012 年在浙大留过学，中文挺溜，刚辞了职一路从欧洲小国独行晃荡到这边。老哥不仅没有留那种刻板的韩式顺毛头，聊起天来也毫无条条框框；而且听他讲我才惊讶地知道，原来韩国普通人对买房的执念也这么深。

今天一天走下来，我觉得布达佩斯的夜景确实很美，它的核心在于一种“概念上的干净”。当然不是说街道卫生干净——它的马路其实破破烂烂的，设施也旧，肯定比不上国内一线城市——而是整个城市的风景和天际线很纯粹。

## 4. 10.28 从布达佩斯到维也纳

在布达佩斯的最后一天，主打一个查漏补缺。

早起天特别蓝，多瑙河上还有大爷在划船。趁着盖勒特山重新开放，爬上山顶站到了雕像脚下，把前几天晚上只能远远仰望的视角给兑现了。下山去圣伊什特万圣殿转了转，又去中央市场吃了特产的花瓣冰淇淋。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/MbknbTgNVoNX95xEW3lcJ9fPnff.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="大水！" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/DpDDbmiVpoH6cYxiAUzcaMwdnaf.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="梦回天津" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/YeCZbcNEroAxdlxihKucv5mfnrf.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="到达布达佩斯最高点" %}
  </div>
</div>

在候车和逛街的时候突然反应过来一个统计学真相：前两天我总觉得布达佩斯满大街都是长相出众的俊男靓女，今天走远了才发现并不是人人都长那样——单纯是因为我住的地方旁边刚好有两所大学，属于典型的样本偏差。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/I4MIbweXSokoLLx4G01cI7FlnMh.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/HIKhbWargox5zBxUxoycHimAnEb.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/HZq9bW1pvoGz8JxfUSsc0lJ0nMh.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

下午和 rf 博 Coffee Chat 了一下，了解了一下现在北美大组都在做什么、是什么运作状态，获取了不少新鲜的 Context。聊完看时间差不多，就回住处取了行李去火车站，坐火车去维也纳。

车票我最开始是在 Klook 上看的，后来发现微信小程序买更便宜（官方 App 用 Apple Pay 死活付不过去）。上车发现都是指定席位，列车员走过去看座位上有人，甚至都不会核验你的证件和车票。我那个包厢里除了我之外就只有一对外国情侣，不得不说外国人真是随时随地都能旁若无人地亲起来。另外，这趟车被人戏称为“喂猪专列”确实没叫错，餐车上的食物非常便宜，味道居然也还过得去。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/NElIb65WiohraTxWWZbcAV3hnlg.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="味道一般" %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/TX7AbmchDoH8XXxXOxGcjyXHn2f.jpg" class="img-fluid rounded z-depth-1" zoomable=true caption="只要1.3欧，太便宜了，甚至还有0.5的芝士蛋糕" %}
  </div>
</div>

晚上抵达维也纳中央车站，一下车那种强烈的反差感就扑面而来。如果说布达佩斯像北京略显荒凉的远郊，那维也纳车站就瞬间把人拉回了繁华的现代化市区（后面几天才深刻体会到，这两座城市的商业繁荣度和基建水平确实完全不在一个 Level 上）。车站很大很新，轨道交通的动线跟国内地铁不太一样，我站在那儿研究了半天，最后还是问了一个看着像学生的年轻小哥，才搞明白怎么坐 S 线去住处。

## 5. 10.29 维也纳 🌧️

早起是个阴雨天。虽然攻略上都说维也纳得逛三天两晚，但如果你体力好、步子快，其实两天就完全够了。

白天顺着小红书上的经典 City Walk 路线在老城区暴走。维也纳确实配得上“艺术之都”的名号，满街的石头建筑很高大，设计感拉满（有一说一，这种高大的石头建筑在视觉冲击力上确实比木质建筑看着更高级，可能还是高大的建筑带给人的压迫感）。中午随便进了家麦当劳解决，这边的麦当劳出餐快得离谱，我点的套餐居然 1 分钟就做好了，端盘子的服务员是印度老哥，看来无论从哪个指标看，奥地利确实都比匈牙利发达得多。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/QBt1bFpOro9GrPxoifgcZJYanre.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/AJ1kbDkhdoIjDFxgZh8cRtmUn3d.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Hu0ZbjQD8ohnWRxyXzKc3E4Nngc.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

顺路去吃了茜茜公主经常吃的皇帝煎饼，打卡了奥地利国家图书馆、霍夫堡，接着扎进了艺术史博物馆。博物馆的馆藏丰富得惊人，而且很多展品离人的物理距离非常近（馆里居然还能看到木乃伊）。逛了整整三个小时，非常值回票价。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/VEmPb8621owoRgx93BqcC1t5n3d.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/ORP5bToN6onuOIx7DIwcRBxBnWc.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/YMSibxEmjojFyzxxmzjczQJBnBf.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/M4ZhbHQQwoO8VwxPp47cQXTlnof.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/SJB6bFt1Jo1MwTxjGi0cvkIMnwf.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/QXAtb0xHFoU7EcxuA4ec4s4onHb.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/QOMIblfq0oF6UPxtdszcwT45nxd.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/SGQAbgusCoda6Ax2e3Mcss13nug.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

晚上去了一家小红书推荐的餐厅，墙上密密麻麻摆满了世界各地的啤酒瓶，放大看还有中国的啤酒。我平时基本滴酒不沾，但本着“来都来了”的心态，还是点了一杯尝尝。吃完饭走到卡尔教堂发现已经关门了，因为这片建筑都是连着的，就顺着街区一路 Walk through 到了奥地利国会大厦。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/SLDnb0G53oPjLExSMxScDYY0ntE.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/RFgzbt18yoLiiCxh1Wmc7iNDnQe.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/NELWbSFCZoaDlhx8x0vcV5Tsnqc.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

国会大厦绝对是来奥地利必看的景点，比许多景点的开放程度高太多了。里面的讲解员全都是政府议会办公室的工作人员，那口英文是我这趟欧洲之行（甚至算上高中去英国那次）听过最标准、最舒服的英文。哪怕我长期不处在英语环境里、听说能力大幅退化，也能完全跟上她的节奏，听她娓娓道来整座建筑背后奥地利民主法治的演变。印象最深的是会议室里有一幅画，站在不同角度看会呈现出完全不同的颜色，用来时刻提醒议员们要“换位思考”。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/UcdSbTQ59oNeeoxKP3mcbHCknlg.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/WiLRbEGh1oEDVaxs9mbcF2agnyf.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

结果晚上回住处发生了一件极其抓马的事。我在维也纳订的是一家介于青旅和酒店之间的胶囊公寓，跟日本的胶囊还不太一样，它所有的门禁全靠手机 App 控制。我半夜去洗澡的时候脑子一抽没带手机，出来直接被死死锁在了门外。大半夜的连个前台都没有，差点以为今晚只能睡走廊地毯上了。

万幸这时候碰到了一个住这里的台湾老哥（大哥已经博士快毕业了），热心地帮我联系上了酒店人员，前前后后折腾了 1.5 个小时才算把我解救出来。说来也巧，之前去日本旅游打不开柜子的时候，也是个台湾小姐姐借了我 100 日元救急。还好我有随身带点小纪念品的习惯，赶紧送了老哥一份小礼物聊表谢意。

借着这个机会，也跟这位在维也纳生活了很久的台湾老哥深入聊了聊当地的真实生活水平：维也纳虽然绝对收入不算特别高，但房租非常便宜（200欧租一个公寓）；公共交通对长居的人来说更是便宜到不可思议，买年卡平均下来一天只要 1 欧元，比国内很多城市都低。而且交通网极其发达，我住的这地方已经算偏的了，坐车到核心城区也就 30 分钟左右。

不过我必须得狠狠吐槽一下维也纳的轨道交通的准点率！明明列车车体看着比布达佩斯破破烂烂的旧车高级得多，甚至比国内很多地铁造型都新，但晚点和取消简直是家常便饭。有一次我要坐 9:18 的车，结果临时取消了，站台里放了一通德语广播我完全听不懂，只能眼观六路，看见周围当地人纷纷往下走，我也赶紧跟着往对面站台转移；结果换过去又遇上晚点，折腾到 9:33 才到地方。单看通勤的准点率，奥地利铁路还真不如车体破旧的布达佩斯。

## 6. 10.30 维也纳 🏰

今天主要去美泉宫和美景宫。看酒店前台摆上了装饰，才反应过来万圣节快到了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/RpQ9bsJMkoCwHYxrTl2cjMU7nGe.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/UzEtbj5RJog1ToxrGXyc4Bq3n8c.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

说实话，美泉宫这个行宫建筑本身看着挺一般的，甚至感觉还不如布达佩斯的霍夫堡有气势，但它的花园修剪得极其整齐。这跟北京秋天的公园很不一样：北京的秋景总还带着点夏天争奇斗艳的劲儿，红叶、黄叶和坚挺的绿树混在一起，很有层次；而美泉宫的树颜色非常统一，就是给你一种确定性的、明明确确的“秋”的感觉。顺着花园一路爬到山顶的凯旋门，在上面喝了杯咖啡，俯瞰维也纳。因为维也纳整体建筑比布达佩斯高，所以并没有“一览众山小”的震撼，但吹吹风还算惬意。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/QyMsbOfeQoJnlHxwzs7cRkNRnDr.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/GbyhbDDtnovWxKxbnUVcKSTAneb.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/JzwQbUkccozTsGxRBlcc0dYanfd.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

下午在飞猪上临时买了美景宫的票。因为平台出票的场次时间没法提前进，干脆就在花园里来回瞎转悠。我实在没什么艺术细胞，进去看画也就是草草略过。

从美景宫出来看时间还早，跑去邮局想买点纪念邮票。结果邮局大叔一脸遗憾地跟我说，我想买的施华洛世奇联名款，昨天刚被一帮上海来的游客给包圆买光了。不过大叔人很好，极力给我推荐了 Albertina 新出的联名邮票——上面印的是丢勒的名画《野兔》。因为这幅画本身材质太脆弱，现在已经不再公开展出了，能买张邮票留作纪念也挺好。大叔还千叮咛万嘱咐，劝我明天一定得去一趟阿尔贝蒂娜博物馆。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/IlvdbfWBWoHHQixVukrc9ndln9d.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/HieIbrYB7oqRzNxy8kUccGRInhg.jpg" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/PCV8bBUw1oIPyvxYxXbcphwonFf.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

晚饭随便吃了顿快餐（这边点快餐居然还非得挨个问你有没有过敏症状，非常神奇），又去超市买了罐挂壁水。接近六点的时候，紧赶慢赶去打卡了莫比乌斯环又转战卡尔教堂。当时正好赶上做弥撒的时间，坐在里面听了一会儿，就奔向今天最重要的目的地——维也纳金色大厅。

去之前我特意让 Gemini 帮我查了近期的排期，挑了今晚这场：不是那种专门糊弄游客的草台班子，而是正经的交响乐团演出。到了现场还有个独自旅行的大叔让我帮忙买票。因为是正经乐团，场内几乎座无虚席，费老大劲才能在角落里找出一两个空位（估计也是买了票临时有事没来的），自然也就没有传闻中的低价赠票环节了。

虽然我对演奏的曲目一窍不通，但一耳朵就能听出来乐团的水准很高。曲子谈不上悠扬，反倒非常激昂；但神奇的是，这么激昂的乐声一点也没打乱我的思绪，反而让我越想越远。可能是一整天暴走下来太累了，再加上明天就要回国，坐在金色大厅里，脑子里不可避免地开始放电影，把这段时间关于工作、去留、人生意义的乱七八糟的念头又通通翻出来想了一遍。

## 7. 10.31 返程 🥶

最后一天正好是周六。因为昨天邮局大爷强烈安利，加上原本计划三天的行程两天就走完了，就准备去 Albertina，但是时间尚早就先去逛了只有周六才开的跳蚤市场。

市场里确实摆着很多杂七杂八、稀奇古怪的老物件，但客观来说要价实在离谱，随便一个做工粗糙的工艺品就敢开口要三四十欧，比在景点纪念品商店买还黑。我在第一家摊位试着对半砍价，没想到摊主一口就答应了，害我当时心里直犯嘀咕，怀疑自己是不是砍一半也当了冤大头。结果后面逛了一圈发现，别人家的东西是真的贵且根本不讲价。我后来又偷偷绕回第一家观察了一下，发现那个卖给我东西的大叔估计有五六十岁了，这么冷的天，身上穿的棉袄都破洞漏出棉花了。大清早的，他大概也是想赶紧做成第一单开个张吧，这么一想，也算是日行一善了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Yfelbwjl3o3L6qxZCZncejL6n7d.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/D7b6bLxhzoYziExuPX8cuDPmnrb.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/I3ljbBaGgoL4iwxpKNccZIVqnfd.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/XSMMbGBCyo2Ubtx7KxScUn6KnXg.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

中午去吃了家本地榜单排名靠前的餐厅（门头上写了一堆德语，拿翻译软件一拍，大概就是维也纳本地“大众点评必吃榜”的意思）。店里本来需要预约，服务员是个看起来像电影里睿智长者一样的黑人大叔，帮我看了一眼发现正好有一桌预约的客人来得晚，看我来得早，就爽快地让我先吃。炸猪排做得挺不错，就是牛肉汤里居然没有牛肉，挺奇怪的。结账的时候不知道是不是看我是中国人，大叔直接帮我跳过了选小费的界面。

下午消食路过了电影《爱在黎明破晓前》取景的桥（虽然我根本没看过这电影，毫无波澜），然后顺着环城大道往阿尔贝蒂娜博物馆走，半路还在奥迪展厅围观了一下 F1 的概念车。

进到阿尔贝蒂娜博物馆，很难得地没看到什么中国游客，估计确实不算国内的热门网红打卡地。虽然前一天在艺术史博物馆看画已经看得有些审美疲劳，但不得不承认，这里展出的大师名作，单纯从欣赏美的角度来看依然让人惊艳。之前听人开玩笑说，做科研的人应该从大师名画里学习怎么给论文画图配色——真希望有朝一日 AI Agent 能自己学会这项技能，毕竟我已经很久没有亲自动手画过图了。

<div class="row mt-3">
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/LBbGbE89VofOPHxnk73cdriLnUd.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/DXkJbIN2loeATQxyX0FcFGTVnRb.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/TOTvbiUsLoEepAxUnoQcfyj0nAg.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
  <div class="col-sm mt-3 mt-md-0">
    {% include figure.liquid url="https://picoflmq.oss-cn-beijing.aliyuncs.com/typora/emnlp2026/Hc2cbQn9hocrLmx760ccRiCtnmH.png" class="img-fluid rounded z-depth-1" zoomable=true %}
  </div>
</div>

傍晚去超市采购土特产。买莫扎特巧克力酒的时候，收银台小哥盯着我看半天，非要查我的 ID，说我看着太年轻了不像成年人。我说我是来布达佩斯开会的，掏出 Passport 给他看，他算完年份发现我已经二十好几了，露出一脸难以置信的表情。老外大概是真的分不清亚洲人的长相和年龄。

拿上寄存的行李去维也纳机场。小红书上有人制造焦虑说机场要排很久，但实际体验下来，维也纳机场的效率比布达佩斯高太多了，托运、值机、安检一路丝滑。 回程的飞机上用上了星链（Starlink），不得不感慨跨洋航班真是星链最大的应用场景。

## 尾声

可能是太久没有这种每天少则两万步、多则近四万步的高强度拉练了，回国第一天直接昏睡到中午十二点才醒。一睁眼，微信上又是导师发来的一堆乱七八糟的消息。匆匆回复完，收拾收拾，又得去搬砖了。

回头想想这两座城市：布达佩斯留给我的底色是一种概念上的“干净”——虽说街道和设施有些陈旧，但整座城市的风景和天际线透彻开阔，像极了北京的秋天，有种说不出来的疏朗感；而维也纳则完全是另一个维度的繁华，整座城市都被浓郁的艺术与文艺气息包裹着。

但不管怎么说，这趟出去走了一圈，看到了美丽的风景，拿到了平时接触不到的 Context，更重要的是在一个陌生的环境里重新审视了自己。既然已经重新感受到了钉子的痛感，接下来，就该真正站起身来了。
