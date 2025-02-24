"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[4452],{3574:(e,s,n)=>{n.r(s),n.d(s,{assets:()=>l,contentTitle:()=>a,default:()=>h,frontMatter:()=>i,metadata:()=>t,toc:()=>c});const t=JSON.parse('{"id":"Moderation/Features/Messages","title":"Message Moderation","description":"The Message Moderation feature helps ensure that users interact with Dollar in the correct channels and prevents misuse by enforcing channel-specific command usage. It also handles Direct Messages (DMs) to the bot and checks for unauthorized or misplaced commands.","source":"@site/docs/4-Moderation/2-Features/Messages.md","sourceDirName":"4-Moderation/2-Features","slug":"/Moderation/Features/Messages","permalink":"/DollarDiscordBot/docs/Moderation/Features/Messages","draft":false,"unlisted":false,"tags":[],"version":"current","frontMatter":{},"sidebar":"tutorialSidebar","previous":{"title":"Inactivity Timeout","permalink":"/DollarDiscordBot/docs/Moderation/Features/Inactivity"},"next":{"title":"Overview of Context Menu Commands","permalink":"/DollarDiscordBot/docs/Context Menu/overview"}}');var r=n(4848),o=n(8453);const i={},a="Message Moderation",l={},c=[{value:"Purpose",id:"purpose",level:2},{value:"How It Works",id:"how-it-works",level:2},{value:"Usage",id:"usage",level:3},{value:"Important Notes",id:"important-notes",level:3}];function d(e){const s={code:"code",h1:"h1",h2:"h2",h3:"h3",header:"header",li:"li",ol:"ol",p:"p",strong:"strong",ul:"ul",...(0,o.R)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(s.header,{children:(0,r.jsx)(s.h1,{id:"message-moderation",children:"Message Moderation"})}),"\n",(0,r.jsxs)(s.p,{children:["The ",(0,r.jsx)(s.strong,{children:"Message Moderation"})," feature helps ensure that users interact with ",(0,r.jsx)(s.strong,{children:"Dollar"})," in the correct channels and prevents misuse by enforcing channel-specific command usage. It also handles Direct Messages (DMs) to the bot and checks for unauthorized or misplaced commands."]}),"\n",(0,r.jsx)(s.h2,{id:"purpose",children:"Purpose"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:["The ",(0,r.jsx)(s.strong,{children:"Message Moderation"})," feature makes sure that all bot commands are issued in the correct text channels."]}),"\n",(0,r.jsx)(s.li,{children:"It prevents bot commands from being used outside of designated command channels, keeping the server organized."}),"\n",(0,r.jsx)(s.li,{children:"It also manages messages in Direct Messages (DMs) to Dollar, ensuring users are aware of how to use the bot."}),"\n",(0,r.jsx)(s.li,{children:"It provides notifications for game updates in specific channels to keep the community informed."}),"\n"]}),"\n",(0,r.jsx)(s.h2,{id:"how-it-works",children:"How It Works"}),"\n",(0,r.jsxs)(s.ol,{children:["\n",(0,r.jsxs)(s.li,{children:["\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Direct Messages (DMs)"}),": If a user sends a DM to ",(0,r.jsx)(s.strong,{children:"Dollar"}),", the bot responds with a welcome message and a link to the README, ensuring that users know how to interact with the bot."]}),"\n"]}),"\n",(0,r.jsxs)(s.li,{children:["\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Game Update Notifications"}),": If a game update is posted in the designated ",(0,r.jsx)(s.strong,{children:"#patches"})," channel, ",(0,r.jsx)(s.strong,{children:"Dollar"})," will automatically detect the update and send notifications to users subscribed to game updates."]}),"\n"]}),"\n",(0,r.jsxs)(s.li,{children:["\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Bot Commands in Correct Channels"}),":"]}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Dollar"})," checks whether the message is sent in the appropriate command channels (e.g., ",(0,r.jsx)(s.code,{children:"#commands"}),", ",(0,r.jsx)(s.code,{children:"dollar-dev"}),")."]}),"\n",(0,r.jsx)(s.li,{children:"If a bot command is used in one of these channels, the bot processes the command as usual."}),"\n"]}),"\n"]}),"\n",(0,r.jsxs)(s.li,{children:["\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Command Misuse"}),":"]}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:["If a user enters a bot command in an incorrect channel (not the designated command channels), ",(0,r.jsx)(s.strong,{children:"Dollar"})," will delete the message and send the user a reminder to use the correct channel."]}),"\n",(0,r.jsx)(s.li,{children:"The bot will notify the user through DM about the mistake and request they use the correct channel for commands."}),"\n"]}),"\n"]}),"\n",(0,r.jsxs)(s.li,{children:["\n",(0,r.jsxs)(s.p,{children:[(0,r.jsx)(s.strong,{children:"Clear Command"}),": The ",(0,r.jsx)(s.code,{children:"!clear"})," command is also processed even if it is used in an incorrect channel, but a warning is logged for the admin's reference."]}),"\n"]}),"\n"]}),"\n",(0,r.jsx)(s.h3,{id:"usage",children:"Usage"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Dollar"})," monitors all incoming messages and determines whether they are bot commands or general chat."]}),"\n",(0,r.jsx)(s.li,{children:"If a bot command is used, it is processed only if the message is sent in the correct channel. If it's misused, the message will be deleted, and the user will be warned via DM."}),"\n"]}),"\n",(0,r.jsx)(s.h3,{id:"important-notes",children:"Important Notes"}),"\n",(0,r.jsxs)(s.ul,{children:["\n",(0,r.jsxs)(s.li,{children:["Direct Messages to ",(0,r.jsx)(s.strong,{children:"Dollar"})," are always responded to with a link to the README, providing users with necessary information about how to interact with the bot."]}),"\n",(0,r.jsxs)(s.li,{children:[(0,r.jsx)(s.strong,{children:"Dollar"})," checks each command's context to ensure it is being used in the appropriate channels, preventing clutter in non-command channels."]}),"\n",(0,r.jsx)(s.li,{children:"Misplaced commands are deleted, and users are gently reminded to follow the rules of the server."}),"\n"]}),"\n",(0,r.jsxs)(s.p,{children:["The ",(0,r.jsx)(s.strong,{children:"Message Moderation"})," feature helps maintain an organized environment where bot commands are used correctly, ensuring a smooth and streamlined experience for users and administrators alike."]})]})}function h(e={}){const{wrapper:s}={...(0,o.R)(),...e.components};return s?(0,r.jsx)(s,{...e,children:(0,r.jsx)(d,{...e})}):d(e)}},8453:(e,s,n)=>{n.d(s,{R:()=>i,x:()=>a});var t=n(6540);const r={},o=t.createContext(r);function i(e){const s=t.useContext(o);return t.useMemo((function(){return"function"==typeof e?e(s):{...s,...e}}),[s,e])}function a(e){let s;return s=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:i(e.components),t.createElement(o.Provider,{value:s},e.children)}}}]);