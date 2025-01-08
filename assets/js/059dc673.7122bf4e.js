"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[196],{2069:(e,n,s)=>{s.r(n),s.d(n,{assets:()=>a,contentTitle:()=>l,default:()=>h,frontMatter:()=>i,metadata:()=>r,toc:()=>d});const r=JSON.parse('{"id":"Context Menu/Commands/UserInfo","title":"User Information","description":"The User Information context menu command allows users to view detailed information about another member in the Discord server. It provides insights into the user\'s account, server activity, and roles in an easy-to-read embed format.","source":"@site/docs/5-Context Menu/2-Commands/UserInfo.md","sourceDirName":"5-Context Menu/2-Commands","slug":"/Context Menu/Commands/UserInfo","permalink":"/DollarDiscordBot/docs/Context Menu/Commands/UserInfo","draft":false,"unlisted":false,"tags":[],"version":"current","frontMatter":{},"sidebar":"tutorialSidebar","previous":{"title":"Poke User","permalink":"/DollarDiscordBot/docs/Context Menu/Commands/PokeUser"}}');var o=s(4848),t=s(8453);const i={},l="User Information",a={},d=[{value:"Purpose",id:"purpose",level:2},{value:"How It Works",id:"how-it-works",level:2},{value:"Usage",id:"usage",level:2},{value:"Example Output",id:"example-output",level:3},{value:"Embed Content:",id:"embed-content",level:4},{value:"Important Notes",id:"important-notes",level:2}];function c(e){const n={code:"code",h1:"h1",h2:"h2",h3:"h3",h4:"h4",header:"header",li:"li",ol:"ol",p:"p",strong:"strong",ul:"ul",...(0,t.R)(),...e.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(n.header,{children:(0,o.jsx)(n.h1,{id:"user-information",children:(0,o.jsx)(n.code,{children:"User Information"})})}),"\n",(0,o.jsxs)(n.p,{children:["The ",(0,o.jsx)(n.strong,{children:"User Information"})," context menu command allows users to view detailed information about another member in the Discord server. It provides insights into the user's account, server activity, and roles in an easy-to-read embed format."]}),"\n",(0,o.jsx)(n.h2,{id:"purpose",children:"Purpose"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsx)(n.li,{children:"Quickly retrieve key information about a server member."}),"\n",(0,o.jsx)(n.li,{children:"Useful for moderators or members looking to learn more about others in the community."}),"\n"]}),"\n",(0,o.jsx)(n.h2,{id:"how-it-works",children:"How It Works"}),"\n",(0,o.jsxs)(n.p,{children:["When you use the ",(0,o.jsx)(n.strong,{children:"User Information"})," command:"]}),"\n",(0,o.jsxs)(n.ol,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Dollar"})," collects the following details about the selected user:","\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Username and Preferred Name"}),": Their username and display name in the server."]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Account Creation Date"}),": When their Discord account was created."]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Server Join Date"}),": When they joined the current Discord server."]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Roles"}),": A list of all roles assigned to the user."]}),"\n"]}),"\n"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Dollar"})," compiles this information into a visually appealing embed."]}),"\n",(0,o.jsx)(n.li,{children:"The bot sends the embed as a response to your command."}),"\n"]}),"\n",(0,o.jsx)(n.h2,{id:"usage",children:"Usage"}),"\n",(0,o.jsxs)(n.ol,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Right-Click on a User"}),": Locate the user whose information you want to view."]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Navigate to Apps > User Information"}),": Select the context menu command."]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Result"}),": Dollar sends an embed message with the user\u2019s details."]}),"\n"]}),"\n",(0,o.jsx)(n.h3,{id:"example-output",children:"Example Output"}),"\n",(0,o.jsx)(n.p,{children:'If you request information for a user named "Jordan," the bot might generate the following embed:'}),"\n",(0,o.jsx)(n.h4,{id:"embed-content",children:"Embed Content:"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"User"}),": Jordan#1234"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Preferred Name"}),": J-Dawg"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Created Their Account"}),": January 10, 2020, at 3:15 PM"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Joined This Discord"}),": June 5, 2021, at 2:30 PM"]}),"\n",(0,o.jsxs)(n.li,{children:[(0,o.jsx)(n.strong,{children:"Roles"}),": Admin, Moderator, Verified"]}),"\n"]}),"\n",(0,o.jsx)(n.p,{children:"The embed will also include:"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsx)(n.li,{children:"The user's avatar (if available)."}),"\n",(0,o.jsx)(n.li,{children:"A footer showing who requested the information."}),"\n"]}),"\n",(0,o.jsx)(n.h2,{id:"important-notes",children:"Important Notes"}),"\n",(0,o.jsxs)(n.ul,{children:["\n",(0,o.jsxs)(n.li,{children:["The command provides ",(0,o.jsx)(n.strong,{children:"read-only information"}),"\u2014no changes can be made to the user's account or roles using this feature."]}),"\n",(0,o.jsx)(n.li,{children:"The information is retrieved from Discord's servers, ensuring accuracy and up-to-date details."}),"\n",(0,o.jsx)(n.li,{children:"Only roles visible to you or allowed by server permissions are shown."}),"\n"]}),"\n",(0,o.jsxs)(n.p,{children:["The ",(0,o.jsx)(n.strong,{children:"User Information"})," command enhances community management by offering an efficient way to access member details, promoting transparency and collaboration within the server."]})]})}function h(e={}){const{wrapper:n}={...(0,t.R)(),...e.components};return n?(0,o.jsx)(n,{...e,children:(0,o.jsx)(c,{...e})}):c(e)}},8453:(e,n,s)=>{s.d(n,{R:()=>i,x:()=>l});var r=s(6540);const o={},t=r.createContext(o);function i(e){const n=r.useContext(t);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:i(e.components),r.createElement(t.Provider,{value:n},e.children)}}}]);