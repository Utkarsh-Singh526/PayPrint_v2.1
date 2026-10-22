// PayPrint Admin Workspace. Configure API_BASE for your environment before deployment.
const API_BASE = "http://10.232.196.179:8000";
const TOKEN_KEY = "payprint_admin_token";
const ROLE_KEY = "payprint_admin_role";
const PROFILE_KEY = "payprint_admin_profile";
const state = { me:null, admins:[], kiosks:[], assignments:[], overview:null, view:"overview", language:localStorage.getItem("payprint_language") || "en", pendingRemoval:null, voiceRecognition:null };
const $ = id => document.getElementById(id);
const translations = {
en:{
workspace:"WORKSPACE",overview:"Overview",admins:"Admins",kiosks:"Kiosks",assignments:"Assignments",needHelp:"Need help?",helpCaption:"Use the voice assistant",signOut:"Sign out",controlCenter:"PAYPRINT CONTROL CENTER",connected:"Workspace",voiceAssistant:"Voice assistant",refresh:"Refresh",loading:"Loading your workspaceâ€¦",welcome:"WELCOME TO PAYPRINT",businessSummary:"Business summary",summaryCaption:"Live information from your PayPrint backend.",totalJobs:"Total print jobs",paidRevenue:"Paid revenue",paidPayments:"Paid payments",confirmedRecords:"Confirmed paid records",totalUsers:"Total users",registeredAccounts:"Registered accounts",printOperations:"Print operations",operationsCaption:"Current job statuses from the database.",pending:"Pending",queued:"Queued",printing:"Printing",completed:"Completed",failed:"Failed",jobBreakdown:"Job status breakdown",breakdownCaption:"Distribution by recorded status.",kioskNetwork:"Kiosk network",kioskNetworkCaption:"Heartbeat-based online status.",activeKiosks:"Active kiosks",onlineNow:"Online now",heartbeatNote:"Online status depends on kiosk heartbeat updates.",recentJobs:"Recent print jobs",recentCaption:"Latest jobs returned by the API.",jobId:"Job ID",created:"Created",kiosk:"Kiosk",pages:"Pages",amount:"Amount",payment:"Payment",status:"Status",adminWorkspaceTitle:"Administrator workspace",adminWorkspaceText:"Your access is limited to kiosks assigned to your account. Super Admin controls are hidden.",adminDirectory:"Admin directory",adminDirectoryCaption:"Create regular admins and review their access.",addAdmin:"Add admin",searchAdmins:"Search by name or email",reloadList:"Reload list",admin:"Admin",email:"Email",role:"Role",accountStatus:"Account status",noAdmins:"No regular admins found",noAdminsCaption:"Create an admin to begin assigning kiosks.",kioskDirectory:"Kiosk directory",kioskDirectoryCaption:"Review registered PayPrint devices.",searchKiosks:"Search kiosk name, ID or location",noKiosks:"No kiosks found",noKiosksCaption:"Registered kiosks will appear here.",assignmentTitle:"Kiosk assignments",assignmentCaption:"Control which regular admin can access each kiosk.",assignKiosk:"Assign kiosk",activeAssignments:"Active assignments",assignmentSecurity:"Only Super Admins can change assignments.",kioskCode:"Kiosk code",action:"Action",noAssignments:"No assignments yet",noAssignmentsCaption:"Assign a kiosk to a regular admin to set their access scope.",footerSecurity:"Role-based access Â· Secure API session",newAdmin:"NEW ADMIN",createRegularAdmin:"Create regular admin",createAdminCaption:"A new admin can only access kiosks assigned to them.",fullName:"Full name",emailLabel:"Email address",temporaryPassword:"Temporary password",passwordHint:"Share credentials securely and ask the admin to change their password if your backend supports it.",cancel:"Cancel",createAdmin:"Create admin",accessControl:"ACCESS CONTROL",assignKioskTitle:"Assign a kiosk",assignKioskCaption:"Choose a regular admin and a kiosk by its internal database ID.",regularAdmin:"Regular admin",kioskIdHint:"The assignment API expects the kiosk's internal numeric ID, not the public kiosk code.",saveAssignment:"Save assignment",removeAssignment:"Remove assignment?",removeAssignmentCaption:"This removes this admin's assignment to the selected kiosk. It does not delete the admin or kiosk.",remove:"Remove",voiceReady:"Ready to help",voiceIntro:"You can ask for help with admins, kiosks or assignments. Browser voice support varies.",readSummary:"Read page summary",listen:"Listen",signInTitle:"Sign in to your workspace",signInSubtitle:"Use your PayPrint administrator credentials to continue.",passwordLabel:"Password",signIn:"Sign in",secureNote:"Protected access. Your permissions depend on your administrator role.",overviewSubtitle:"Your print network at a glance.",welcomeTitle:"Your operations, in one place.",welcomeText:"Monitor your printing network and keep your kiosks organized.",adminScope:"Your account is active. Use only the kiosks assigned to you.",loginExpired:"Session expired or login required. Please sign in again.",superOnly:"Super Admin access is required.",loadingAdmins:"Loading adminsâ€¦",loadingKiosks:"Loading kiosksâ€¦",loadingAssignments:"Loading assignmentsâ€¦",active:"Active",inactive:"Inactive",removeAssignmentAction:"Remove",noSearchResults:"No results match your search.",createSuccess:"Regular admin created successfully.",assignSuccess:"Kiosk assigned successfully.",removeSuccess:"Assignment removed successfully.",voiceUnsupported:"Voice input is not supported in this browser. Try a current Chrome or Edge browser.",voiceListening:"Listeningâ€¦ say â€œadminsâ€, â€œkiosksâ€, â€œassignmentsâ€ or â€œoverviewâ€.",voicePermission:"Microphone permission may be required.",unknownVoice:"I did not recognize that command. Try â€œopen adminsâ€ or â€œread summaryâ€.",confirmRemove:"Remove this assignment?",adminCount:"regular admins",kioskCount:"kiosks",assignmentCountLabel:"assignments",loginFallbackWarning:"This backend accepts login credentials in a query string, which can expose them in server logs. Prefer POST /auth/login-json."
},
hi:{
workspace:"à¤•à¤¾à¤°à¥à¤¯ à¤•à¥à¤·à¥‡à¤¤à¥à¤°",overview:"à¤“à¤µà¤°à¤µà¥à¤¯à¥‚",admins:"à¤à¤¡à¤®à¤¿à¤¨",kiosks:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤•",assignments:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ",needHelp:"à¤®à¤¦à¤¦ à¤šà¤¾à¤¹à¤¿à¤?",helpCaption:"à¤µà¥‰à¤‡à¤¸ à¤…à¤¸à¤¿à¤¸à¥à¤Ÿà¥‡à¤‚à¤Ÿ à¤‡à¤¸à¥à¤¤à¥‡à¤®à¤¾à¤² à¤•à¤°à¥‡à¤‚",signOut:"à¤¸à¤¾à¤‡à¤¨ à¤†à¤‰à¤Ÿ",controlCenter:"PAYPRINT à¤•à¤‚à¤Ÿà¥à¤°à¥‹à¤² à¤¸à¥‡à¤‚à¤Ÿà¤°",connected:"à¤µà¤°à¥à¤•à¤¸à¥à¤ªà¥‡à¤¸",voiceAssistant:"à¤µà¥‰à¤‡à¤¸ à¤…à¤¸à¤¿à¤¸à¥à¤Ÿà¥‡à¤‚à¤Ÿ",refresh:"à¤°à¤¿à¤«à¥à¤°à¥‡à¤¶",loading:"à¤µà¤°à¥à¤•à¤¸à¥à¤ªà¥‡à¤¸ à¤²à¥‹à¤¡ à¤¹à¥‹ à¤°à¤¹à¤¾ à¤¹à¥ˆâ€¦",welcome:"PAYPRINT à¤®à¥‡à¤‚ à¤†à¤ªà¤•à¤¾ à¤¸à¥à¤µà¤¾à¤—à¤¤ à¤¹à¥ˆ",businessSummary:"à¤¬à¤¿à¤œà¤¼à¤¨à¥‡à¤¸ à¤¸à¤¾à¤°à¤¾à¤‚à¤¶",summaryCaption:"à¤†à¤ªà¤•à¥‡ PayPrint à¤¬à¥ˆà¤•à¤à¤‚à¤¡ à¤¸à¥‡ à¤²à¤¾à¤‡à¤µ à¤œà¤¾à¤¨à¤•à¤¾à¤°à¥€à¥¤",totalJobs:"à¤•à¥à¤² à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤œà¥‰à¤¬",paidRevenue:"à¤•à¥à¤² à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤°à¤¾à¤¶à¤¿",paidPayments:"à¤¸à¤«à¤² à¤­à¥à¤—à¤¤à¤¾à¤¨",confirmedRecords:"à¤•à¤¨à¥à¤«à¤°à¥à¤® à¤­à¥à¤—à¤¤à¤¾à¤¨ à¤°à¤¿à¤•à¥‰à¤°à¥à¤¡",totalUsers:"à¤•à¥à¤² à¤¯à¥‚à¤œà¤¼à¤°",registeredAccounts:"à¤°à¤œà¤¿à¤¸à¥à¤Ÿà¤°à¥à¤¡ à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ",printOperations:"à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤‘à¤ªà¤°à¥‡à¤¶à¤¨",operationsCaption:"à¤¡à¥‡à¤Ÿà¤¾à¤¬à¥‡à¤¸ à¤®à¥‡à¤‚ à¤®à¥Œà¤œà¥‚à¤¦à¤¾ à¤œà¥‰à¤¬ à¤¸à¥à¤Ÿà¥‡à¤Ÿà¤¸à¥¤",pending:"à¤ªà¥‡à¤‚à¤¡à¤¿à¤‚à¤—",queued:"à¤•à¤¤à¤¾à¤° à¤®à¥‡à¤‚",printing:"à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤¹à¥‹ à¤°à¤¹à¤¾ à¤¹à¥ˆ",completed:"à¤ªà¥‚à¤°à¤¾ à¤¹à¥à¤†",failed:"à¤«à¥‡à¤²",jobBreakdown:"à¤œà¥‰à¤¬ à¤¸à¥à¤Ÿà¥‡à¤Ÿà¤¸ à¤µà¤¿à¤µà¤°à¤£",breakdownCaption:"à¤¸à¥à¤Ÿà¥‡à¤Ÿà¤¸ à¤•à¥‡ à¤…à¤¨à¥à¤¸à¤¾à¤° à¤µà¤¿à¤¤à¤°à¤£à¥¤",kioskNetwork:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¨à¥‡à¤Ÿà¤µà¤°à¥à¤•",kioskNetworkCaption:"à¤¹à¤¾à¤°à¥à¤Ÿà¤¬à¥€à¤Ÿ à¤•à¥‡ à¤†à¤§à¤¾à¤° à¤ªà¤° à¤‘à¤¨à¤²à¤¾à¤‡à¤¨ à¤¸à¥à¤¥à¤¿à¤¤à¤¿à¥¤",activeKiosks:"à¤¸à¤•à¥à¤°à¤¿à¤¯ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤•",onlineNow:"à¤…à¤­à¥€ à¤‘à¤¨à¤²à¤¾à¤‡à¤¨",heartbeatNote:"à¤‘à¤¨à¤²à¤¾à¤‡à¤¨ à¤¸à¥à¤¥à¤¿à¤¤à¤¿ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¹à¤¾à¤°à¥à¤Ÿà¤¬à¥€à¤Ÿ à¤ªà¤° à¤¨à¤¿à¤°à¥à¤­à¤° à¤¹à¥ˆà¥¤",recentJobs:"à¤¹à¤¾à¤² à¤•à¥€ à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤œà¥‰à¤¬",recentCaption:"API à¤¸à¥‡ à¤®à¤¿à¤²à¥€ à¤¹à¤¾à¤² à¤•à¥€ à¤œà¥‰à¤¬à¥¤",jobId:"à¤œà¥‰à¤¬ ID",created:"à¤¬à¤¨à¤¾à¤¯à¤¾ à¤—à¤¯à¤¾",kiosk:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤•",pages:"à¤ªà¥‡à¤œ",amount:"à¤°à¤¾à¤¶à¤¿",payment:"à¤ªà¥‡à¤®à¥‡à¤‚à¤Ÿ",status:"à¤¸à¥à¤¥à¤¿à¤¤à¤¿",adminWorkspaceTitle:"à¤à¤¡à¤®à¤¿à¤¨ à¤µà¤°à¥à¤•à¤¸à¥à¤ªà¥‡à¤¸",adminWorkspaceText:"à¤†à¤ª à¤•à¥‡à¤µà¤² à¤…à¤ªà¤¨à¥‡ à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ à¤•à¥‹ à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤¿à¤ à¤—à¤ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¤à¤• à¤ªà¤¹à¥à¤à¤š à¤¸à¤•à¤¤à¥‡ à¤¹à¥ˆà¤‚à¥¤ Super Admin à¤•à¤‚à¤Ÿà¥à¤°à¥‹à¤² à¤›à¤¿à¤ªà¥‡ à¤¹à¥à¤ à¤¹à¥ˆà¤‚à¥¤",adminDirectory:"à¤à¤¡à¤®à¤¿à¤¨ à¤¸à¥‚à¤šà¥€",adminDirectoryCaption:"Regular Admin à¤¬à¤¨à¤¾à¤à¤ à¤”à¤° à¤‰à¤¨à¤•à¥€ à¤ªà¤¹à¥à¤à¤š à¤¦à¥‡à¤–à¥‡à¤‚à¥¤",addAdmin:"à¤à¤¡à¤®à¤¿à¤¨ à¤œà¥‹à¤¡à¤¼à¥‡à¤‚",searchAdmins:"à¤¨à¤¾à¤® à¤¯à¤¾ à¤ˆà¤®à¥‡à¤² à¤¸à¥‡ à¤–à¥‹à¤œà¥‡à¤‚",reloadList:"à¤¸à¥‚à¤šà¥€ à¤°à¥€à¤²à¥‹à¤¡ à¤•à¤°à¥‡à¤‚",admin:"à¤à¤¡à¤®à¤¿à¤¨",email:"à¤ˆà¤®à¥‡à¤²",role:"à¤°à¥‹à¤²",accountStatus:"à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ à¤¸à¥à¤¥à¤¿à¤¤à¤¿",noAdmins:"à¤•à¥‹à¤ˆ Regular Admin à¤¨à¤¹à¥€à¤‚ à¤®à¤¿à¤²à¤¾",noAdminsCaption:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤ªà¤¹à¤²à¥‡ à¤à¤¡à¤®à¤¿à¤¨ à¤¬à¤¨à¤¾à¤à¤à¥¤",kioskDirectory:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¸à¥‚à¤šà¥€",kioskDirectoryCaption:"à¤°à¤œà¤¿à¤¸à¥à¤Ÿà¤°à¥à¤¡ PayPrint à¤¡à¤¿à¤µà¤¾à¤‡à¤¸ à¤¦à¥‡à¤–à¥‡à¤‚à¥¤",searchKiosks:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¨à¤¾à¤®, ID à¤¯à¤¾ à¤²à¥‹à¤•à¥‡à¤¶à¤¨ à¤–à¥‹à¤œà¥‡à¤‚",noKiosks:"à¤•à¥‹à¤ˆ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¨à¤¹à¥€à¤‚ à¤®à¤¿à¤²à¤¾",noKiosksCaption:"à¤°à¤œà¤¿à¤¸à¥à¤Ÿà¤°à¥à¤¡ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¯à¤¹à¤¾à¤ à¤¦à¤¿à¤–à¥‡à¤‚à¤—à¥‡à¥¤",assignmentTitle:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ",assignmentCaption:"à¤¤à¤¯ à¤•à¤°à¥‡à¤‚ à¤•à¤¿ à¤•à¥Œà¤¨-à¤¸à¤¾ Regular Admin à¤•à¤¿à¤¸ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¤à¤• à¤ªà¤¹à¥à¤à¤š à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆà¥¤",assignKiosk:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤°à¥‡à¤‚",activeAssignments:"à¤¸à¤•à¥à¤°à¤¿à¤¯ à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ",assignmentSecurity:"à¤•à¥‡à¤µà¤² Super Admin à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¬à¤¦à¤² à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆà¥¤",kioskCode:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤•à¥‹à¤¡",action:"à¤à¤•à¥à¤¶à¤¨",noAssignments:"à¤…à¤­à¥€ à¤•à¥‹à¤ˆ à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¨à¤¹à¥€à¤‚",noAssignmentsCaption:"à¤à¤¡à¤®à¤¿à¤¨ à¤•à¥€ à¤ªà¤¹à¥à¤à¤š à¤¤à¤¯ à¤•à¤°à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤°à¥‡à¤‚à¥¤",footerSecurity:"à¤°à¥‹à¤²-à¤†à¤§à¤¾à¤°à¤¿à¤¤ à¤ªà¤¹à¥à¤à¤š Â· à¤¸à¥à¤°à¤•à¥à¤·à¤¿à¤¤ API à¤¸à¥‡à¤¶à¤¨",newAdmin:"à¤¨à¤¯à¤¾ à¤à¤¡à¤®à¤¿à¤¨",createRegularAdmin:"Regular Admin à¤¬à¤¨à¤¾à¤à¤",createAdminCaption:"à¤¨à¤¯à¤¾ à¤à¤¡à¤®à¤¿à¤¨ à¤•à¥‡à¤µà¤² à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤¿à¤ à¤—à¤ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¤à¤• à¤ªà¤¹à¥à¤à¤š à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆà¥¤",fullName:"à¤ªà¥‚à¤°à¤¾ à¤¨à¤¾à¤®",emailLabel:"à¤ˆà¤®à¥‡à¤² à¤ªà¤¤à¤¾",temporaryPassword:"à¤…à¤¸à¥à¤¥à¤¾à¤¯à¥€ à¤ªà¤¾à¤¸à¤µà¤°à¥à¤¡",passwordHint:"à¤•à¥à¤°à¥‡à¤¡à¥‡à¤‚à¤¶à¤¿à¤¯à¤² à¤¸à¥à¤°à¤•à¥à¤·à¤¿à¤¤ à¤¤à¤°à¥€à¤•à¥‡ à¤¸à¥‡ à¤¸à¤¾à¤à¤¾ à¤•à¤°à¥‡à¤‚à¥¤",cancel:"à¤°à¤¦à¥à¤¦ à¤•à¤°à¥‡à¤‚",createAdmin:"à¤à¤¡à¤®à¤¿à¤¨ à¤¬à¤¨à¤¾à¤à¤",accessControl:"à¤à¤•à¥à¤¸à¥‡à¤¸ à¤•à¤‚à¤Ÿà¥à¤°à¥‹à¤²",assignKioskTitle:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤°à¥‡à¤‚",assignKioskCaption:"Regular Admin à¤”à¤° à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤•à¤¾ à¤‡à¤‚à¤Ÿà¤°à¤¨à¤² à¤¡à¥‡à¤Ÿà¤¾à¤¬à¥‡à¤¸ ID à¤šà¥à¤¨à¥‡à¤‚à¥¤",regularAdmin:"Regular Admin",kioskIdHint:"API à¤•à¥‹ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤•à¤¾ à¤‡à¤‚à¤Ÿà¤°à¤¨à¤² à¤¨à¤‚à¤¬à¤° à¤šà¤¾à¤¹à¤¿à¤, à¤ªà¤¬à¥à¤²à¤¿à¤• à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤•à¥‹à¤¡ à¤¨à¤¹à¥€à¤‚à¥¤",saveAssignment:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¸à¥‡à¤µ à¤•à¤°à¥‡à¤‚",removeAssignment:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¹à¤Ÿà¤¾à¤à¤?",removeAssignmentCaption:"à¤‡à¤¸à¤¸à¥‡ à¤à¤¡à¤®à¤¿à¤¨ à¤•à¥€ à¤‡à¤¸ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¤à¤• à¤ªà¤¹à¥à¤à¤š à¤¹à¤Ÿà¥‡à¤—à¥€à¥¤ à¤à¤¡à¤®à¤¿à¤¨ à¤¯à¤¾ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¡à¤¿à¤²à¥€à¤Ÿ à¤¨à¤¹à¥€à¤‚ à¤¹à¥‹à¤—à¤¾à¥¤",remove:"à¤¹à¤Ÿà¤¾à¤à¤",voiceReady:"à¤®à¤¦à¤¦ à¤•à¥‡ à¤²à¤¿à¤ à¤¤à¥ˆà¤¯à¤¾à¤°",voiceIntro:"à¤à¤¡à¤®à¤¿à¤¨, à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¯à¤¾ à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤•à¥‡ à¤¬à¤¾à¤°à¥‡ à¤®à¥‡à¤‚ à¤ªà¥‚à¤›à¥‡à¤‚à¥¤ à¤¬à¥à¤°à¤¾à¤‰à¤œà¤¼à¤° à¤•à¥‡ à¤…à¤¨à¥à¤¸à¤¾à¤° à¤µà¥‰à¤‡à¤¸ à¤¸à¤ªà¥‹à¤°à¥à¤Ÿ à¤…à¤²à¤— à¤¹à¥‹ à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆà¥¤",readSummary:"à¤ªà¥‡à¤œ à¤¸à¤¾à¤°à¤¾à¤‚à¤¶ à¤¸à¥à¤¨à¥‡à¤‚",listen:"à¤¸à¥à¤¨à¥‡à¤‚",signInTitle:"à¤…à¤ªà¤¨à¥‡ à¤µà¤°à¥à¤•à¤¸à¥à¤ªà¥‡à¤¸ à¤®à¥‡à¤‚ à¤¸à¤¾à¤‡à¤¨ à¤‡à¤¨ à¤•à¤°à¥‡à¤‚",signInSubtitle:"à¤œà¤¾à¤°à¥€ à¤°à¤–à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ PayPrint à¤à¤¡à¤®à¤¿à¤¨ à¤•à¥à¤°à¥‡à¤¡à¥‡à¤‚à¤¶à¤¿à¤¯à¤² à¤‡à¤¸à¥à¤¤à¥‡à¤®à¤¾à¤² à¤•à¤°à¥‡à¤‚à¥¤",passwordLabel:"à¤ªà¤¾à¤¸à¤µà¤°à¥à¤¡",signIn:"à¤¸à¤¾à¤‡à¤¨ à¤‡à¤¨",secureNote:"à¤†à¤ªà¤•à¥€ à¤ªà¤°à¤®à¤¿à¤¶à¤¨ à¤†à¤ªà¤•à¥‡ à¤à¤¡à¤®à¤¿à¤¨ à¤°à¥‹à¤² à¤ªà¤° à¤¨à¤¿à¤°à¥à¤­à¤° à¤¹à¥ˆà¥¤",overviewSubtitle:"à¤†à¤ªà¤•à¤¾ à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤¨à¥‡à¤Ÿà¤µà¤°à¥à¤• à¤à¤• à¤¨à¤œà¤¼à¤° à¤®à¥‡à¤‚à¥¤",welcomeTitle:"à¤†à¤ªà¤•à¥‡ à¤¸à¤­à¥€ à¤‘à¤ªà¤°à¥‡à¤¶à¤¨, à¤à¤• à¤œà¤—à¤¹à¥¤",welcomeText:"à¤ªà¥à¤°à¤¿à¤‚à¤Ÿ à¤¨à¥‡à¤Ÿà¤µà¤°à¥à¤• à¤®à¥‰à¤¨à¤¿à¤Ÿà¤° à¤•à¤°à¥‡à¤‚ à¤”à¤° à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤µà¥à¤¯à¤µà¤¸à¥à¤¥à¤¿à¤¤ à¤°à¤–à¥‡à¤‚à¥¤",adminScope:"à¤†à¤ªà¤•à¤¾ à¤…à¤•à¤¾à¤‰à¤‚à¤Ÿ à¤¸à¤•à¥à¤°à¤¿à¤¯ à¤¹à¥ˆà¥¤ à¤•à¥‡à¤µà¤² à¤†à¤ªà¤•à¥‹ à¤…à¤¸à¤¾à¤‡à¤¨ à¤•à¤¿à¤ à¤—à¤ à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤‡à¤¸à¥à¤¤à¥‡à¤®à¤¾à¤² à¤•à¤°à¥‡à¤‚à¥¤",loginExpired:"à¤¸à¥‡à¤¶à¤¨ à¤¸à¤®à¤¾à¤ªà¥à¤¤ à¤¹à¥à¤† à¤¯à¤¾ à¤²à¥‰à¤—à¤¿à¤¨ à¤†à¤µà¤¶à¥à¤¯à¤• à¤¹à¥ˆà¥¤ à¤¦à¥‹à¤¬à¤¾à¤°à¤¾ à¤¸à¤¾à¤‡à¤¨ à¤‡à¤¨ à¤•à¤°à¥‡à¤‚à¥¤",superOnly:"Super Admin à¤•à¥€ à¤…à¤¨à¥à¤®à¤¤à¤¿ à¤†à¤µà¤¶à¥à¤¯à¤• à¤¹à¥ˆà¥¤",loadingAdmins:"à¤à¤¡à¤®à¤¿à¤¨ à¤²à¥‹à¤¡ à¤¹à¥‹ à¤°à¤¹à¥‡ à¤¹à¥ˆà¤‚â€¦",loadingKiosks:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤²à¥‹à¤¡ à¤¹à¥‹ à¤°à¤¹à¥‡ à¤¹à¥ˆà¤‚â€¦",loadingAssignments:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤²à¥‹à¤¡ à¤¹à¥‹ à¤°à¤¹à¥‡ à¤¹à¥ˆà¤‚â€¦",active:"à¤¸à¤•à¥à¤°à¤¿à¤¯",inactive:"à¤¨à¤¿à¤·à¥à¤•à¥à¤°à¤¿à¤¯",removeAssignmentAction:"à¤¹à¤Ÿà¤¾à¤à¤",noSearchResults:"à¤†à¤ªà¤•à¥€ à¤–à¥‹à¤œ à¤¸à¥‡ à¤•à¥‹à¤ˆ à¤ªà¤°à¤¿à¤£à¤¾à¤® à¤¨à¤¹à¥€à¤‚ à¤®à¤¿à¤²à¤¾à¥¤",createSuccess:"Regular Admin à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤¬à¤¨à¤¾à¤¯à¤¾ à¤—à¤¯à¤¾à¥¤",assignSuccess:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤¸à¤«à¤²à¤¤à¤¾à¤ªà¥‚à¤°à¥à¤µà¤• à¤…à¤¸à¤¾à¤‡à¤¨ à¤¹à¥à¤†à¥¤",removeSuccess:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¹à¤Ÿà¤¾ à¤¦à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾à¥¤",voiceUnsupported:"à¤‡à¤¸ à¤¬à¥à¤°à¤¾à¤‰à¤œà¤¼à¤° à¤®à¥‡à¤‚ à¤µà¥‰à¤‡à¤¸ à¤‡à¤¨à¤ªà¥à¤Ÿ à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¨à¤¹à¥€à¤‚ à¤¹à¥ˆà¥¤ à¤¨à¤¯à¤¾ Chrome à¤¯à¤¾ Edge à¤†à¤œà¤¼à¤®à¤¾à¤à¤à¥¤",voiceListening:"à¤¸à¥à¤¨ à¤°à¤¹à¤¾ à¤¹à¥ˆâ€¦ â€œadminsâ€, â€œkiosksâ€, â€œassignmentsâ€ à¤¯à¤¾ â€œoverviewâ€ à¤•à¤¹à¥‡à¤‚à¥¤",voicePermission:"à¤®à¤¾à¤‡à¤•à¥à¤°à¥‹à¤«à¤¼à¥‹à¤¨ à¤•à¥€ à¤…à¤¨à¥à¤®à¤¤à¤¿ à¤†à¤µà¤¶à¥à¤¯à¤• à¤¹à¥‹ à¤¸à¤•à¤¤à¥€ à¤¹à¥ˆà¥¤",unknownVoice:"à¤•à¤®à¤¾à¤‚à¤¡ à¤¸à¤®à¤ à¤¨à¤¹à¥€à¤‚ à¤†à¤¯à¤¾à¥¤ â€œopen adminsâ€ à¤¯à¤¾ â€œread summaryâ€ à¤¬à¥‹à¤²à¥‡à¤‚à¥¤",confirmRemove:"à¤•à¥à¤¯à¤¾ à¤¯à¤¹ à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤¹à¤Ÿà¤¾à¤¨à¤¾ à¤¹à¥ˆ?",adminCount:"Regular Admin",kioskCount:"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤•",assignmentCountLabel:"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ",loginFallbackWarning:"à¤¯à¤¹ à¤¬à¥ˆà¤•à¤à¤‚à¤¡ à¤²à¥‰à¤—à¤¿à¤¨ à¤•à¥à¤°à¥‡à¤¡à¥‡à¤‚à¤¶à¤¿à¤¯à¤² URL query à¤®à¥‡à¤‚ à¤¸à¥à¤µà¥€à¤•à¤¾à¤° à¤•à¤° à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆ, à¤œà¤¿à¤¸à¤¸à¥‡ à¤²à¥‰à¤— à¤®à¥‡à¤‚ à¤ªà¤¾à¤¸à¤µà¤°à¥à¤¡ à¤¦à¤¿à¤– à¤¸à¤•à¤¤à¤¾ à¤¹à¥ˆà¥¤ POST /auth/login-json à¤¬à¥‡à¤¹à¤¤à¤° à¤¹à¥ˆà¥¤"}
};
function t(key){return (translations[state.language]||translations.en)[key]||translations.en[key]||key;}
function token(){return localStorage.getItem(TOKEN_KEY);}
function clearSession(){localStorage.removeItem(TOKEN_KEY);localStorage.removeItem(ROLE_KEY);localStorage.removeItem(PROFILE_KEY);}
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function money(v){return new Intl.NumberFormat(state.language==="hi"?"hi-IN":"en-IN",{style:"currency",currency:"INR",maximumFractionDigits:2}).format(Number(v||0));}
function dateTime(v){if(!v)return "â€”";const d=new Date(v);return Number.isNaN(d.getTime())?"â€”":d.toLocaleString(state.language==="hi"?"hi-IN":"en-IN");}
function setText(id,v){const el=$(id);if(el)el.textContent=v;}
function showToast(message,type=""){const el=$("toast");if(!el)return;el.textContent=message;el.className=`toast ${type}`;if(message)setTimeout(()=>{if(el.textContent===message)el.className="toast";},5000);}
function setError(message){const el=$("pageError");if(el)el.textContent=message||"";}
function apiError(data,status){return data.detail||data.message||`Request failed (${status})`;}
async function api(path,options={}){
  const headers={...(options.headers||{})};if(token())headers.Authorization=`Bearer ${token()}`;
  if(options.body && !(options.body instanceof FormData) && !headers["Content-Type"])headers["Content-Type"]="application/json";
  const response=await fetch(`${API_BASE}${path}`,{...options,headers});
  const data=await response.json().catch(()=>({}));
  if(!response.ok){if(response.status===401){clearSession();if(location.pathname.toLowerCase().endsWith("dashboard.html"))location.replace("login.html");}throw new Error(apiError(data,response.status));}
  return data;
}
function applyLanguage(){
  document.documentElement.lang=state.language==="hi"?"hi":"en";
  document.querySelectorAll("[data-i18n]").forEach(el=>{const key=el.dataset.i18n;el.textContent=t(key);});
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>{el.placeholder=t(el.dataset.i18nPlaceholder);});
  document.querySelectorAll("#langButton").forEach(el=>el.textContent=state.language==="en"?"à¤¹à¤¿à¤¨à¥à¤¦à¥€":"English");
  if($("pageTitle")){const keys={overview:"overview",admins:"admins",kiosks:"kiosks",assignments:"assignments"};setText("pageTitle",t(keys[state.view]||"overview"));setText("pageSubtitle",state.view==="overview"?t("overviewSubtitle"):"");}
}
function switchLanguage(){state.language=state.language==="en"?"hi":"en";localStorage.setItem("payprint_language",state.language);applyLanguage();renderAdmins();renderKiosks();renderAssignments();if(state.overview)renderOverview(state.overview);}
function setView(view){
  if(!["overview","admins","kiosks","assignments"].includes(view))view="overview";
  if(state.me && state.me.role!=="SUPER_ADMIN" && view!=="overview")view="overview";
  state.view=view;document.querySelectorAll(".view-section").forEach(s=>s.hidden=s.id!==`view-${view}`);
  document.querySelectorAll(".nav-link").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
  applyLanguage();closeMobileMenu();setError("");
  if(view==="admins")loadAdmins();if(view==="kiosks")loadKiosks();if(view==="assignments")loadAssignments();
}
function openDialog(id){const d=$(id);if(d?.showModal)d.showModal();else d?.setAttribute("open","");}
function closeDialog(id){const d=$(id);if(d?.close)d.close();else d?.removeAttribute("open");}
function bindCloseButtons(){document.querySelectorAll("[data-close]").forEach(b=>b.addEventListener("click",()=>closeDialog(b.dataset.close)));}
function statusClass(s){const v=String(s||"").toLowerCase();return ["completed","failed","pending","paid","order_created","queued","active","inactive"].includes(v)?v:"";}
function initials(name){return String(name||"PP").trim().split(/\s+/).slice(0,2).map(s=>s[0]?.toUpperCase()||"").join("")||"PP";}

async function loginRequest(email,password){
  // Prefer a JSON-body endpoint so credentials do not appear in the URL or access logs.
  try{return await api("/auth/login-json",{method:"POST",body:JSON.stringify({email,password})});}
  catch(err){
    // Compatibility fallback for the currently documented legacy backend route.
    // This is temporary: query-string passwords may be recorded in server logs.
    if(/404|405|not found|method not allowed/i.test(err.message)){
      const params=new URLSearchParams({email,password});
      return await api(`/auth/login?${params.toString()}`,{method:"POST"});
    }
    throw err;
  }
}
async function initLogin(){
  const form=$("loginForm");if(!form)return;
  applyLanguage();
  $("langButton")?.addEventListener("click",switchLanguage);
  if(token()){
    try{const me=await api("/auth/me");if(me.is_active && ["SUPER_ADMIN","ADMIN","REGULAR_ADMIN"].includes(me.role)){location.replace("dashboard.html");return;}}catch(_){}
    clearSession();
  }
  form.addEventListener("submit",async e=>{
    e.preventDefault();const button=$("loginButton"),error=$("loginError");error.textContent="";button.disabled=true;
    button.innerHTML=`<span>${state.language==="hi"?"à¤¸à¤¾à¤‡à¤¨ à¤‡à¤¨ à¤¹à¥‹ à¤°à¤¹à¤¾ à¤¹à¥ˆâ€¦":"Signing inâ€¦"}</span>`;
    try{
      const email=$("email").value.trim(),password=$("password").value;
      const result=await loginRequest(email,password);
      if(!result.access_token)throw new Error("Login endpoint did not return an access token.");
      localStorage.setItem(TOKEN_KEY,result.access_token);
      const me=await api("/auth/me");
      if(!me.is_active || !["SUPER_ADMIN","ADMIN","REGULAR_ADMIN"].includes(me.role)){clearSession();throw new Error("This account does not have active administrator access.");}
      localStorage.setItem(ROLE_KEY,me.role);localStorage.setItem(PROFILE_KEY,JSON.stringify({name:me.name,email:me.email,role:me.role}));
      location.href="dashboard.html";
    }catch(err){error.textContent=err.message||"Login failed. Check backend connection.";}
    finally{button.disabled=false;button.innerHTML=`<span>${t("signIn")}</span><span aria-hidden="true">â†’</span>`;}
  });
}

async function initDashboard(){
  if(!$("view-overview"))return;
  if(!token()){location.replace("login.html");return;}
  try{
    state.me=await api("/auth/me");
    if(!state.me.is_active||!["SUPER_ADMIN","ADMIN","REGULAR_ADMIN"].includes(state.me.role)){clearSession();location.replace("login.html");return;}
  }catch(err){clearSession();location.replace("login.html");return;}
  setText("adminName",state.me.name|| (state.me.role==="SUPER_ADMIN"?"Super Admin":"Administrator"));
  setText("adminEmail",state.me.email||"Authorized account");setText("avatar",initials(state.me.name||state.me.email));setText("roleChip",state.me.role==="SUPER_ADMIN"?"SUPER ADMIN":"REGULAR ADMIN");
  document.querySelectorAll(".super-only").forEach(el=>el.hidden=state.me.role!=="SUPER_ADMIN");
  $("superMetrics").hidden=state.me.role!=="SUPER_ADMIN";$("superOperations").hidden=state.me.role!=="SUPER_ADMIN";$("regularWelcome").hidden=state.me.role==="SUPER_ADMIN";
  if(state.me.role!=="SUPER_ADMIN"){setText("welcomeTitle",state.language==="hi"?"à¤†à¤ªà¤•à¤¾ à¤à¤¡à¤®à¤¿à¤¨ à¤µà¤°à¥à¤•à¤¸à¥à¤ªà¥‡à¤¸ à¤¤à¥ˆà¤¯à¤¾à¤° à¤¹à¥ˆ":"Your admin workspace is ready.");setText("welcomeText",t("adminScope"));setText("regularScopeNote",t("adminWorkspaceText"));}
  applyLanguage();setView("overview");await loadOverview();
}
async function loadOverview(){
  const loading=$("loading");if(loading){loading.hidden=false;loading.innerHTML=`<span class="spinner"></span><span>${t("loading")}</span>`;}
  setError("");
  try{
    if(state.me.role==="SUPER_ADMIN"){
      const data=await api("/admin/dashboard/overview");state.overview=data;renderOverview(data);
    }else{
      // Management and global metrics APIs are intentionally not called for regular admins.
      // This keeps the UI aligned with the backend's role-based access model.
      $("regularWelcome").hidden=false;
    }
  }catch(err){setError(err.message||"Unable to load dashboard data.");}
  finally{if(loading)loading.hidden=true;}
}
function renderOverview(data){
  if(!$("totalJobs"))return;const m=data.metrics||{};
  setText("totalJobs",m.total_jobs??0);setText("jobsToday",`${m.jobs_today??0} ${state.language==="hi"?"à¤†à¤œ à¤¬à¤¨à¤¾à¤ à¤—à¤":"created today"}`);
  setText("totalRevenue",money(m.total_revenue_inr));setText("revenueToday",`${money(m.revenue_today_inr)} ${state.language==="hi"?"à¤†à¤œ":"today"}`);
  setText("paidPayments",m.paid_payments??0);setText("totalUsers",m.total_users??0);setText("pendingJobs",m.pending_jobs??0);setText("queuedJobs",m.queued_jobs??0);setText("printingJobs",m.printing_jobs??0);setText("completedJobs",m.completed_jobs??0);setText("failedJobs",m.failed_jobs??0);
  setText("totalKiosks",m.total_kiosks??0);setText("activeKiosks",m.active_kiosks??0);setText("onlineKiosks",m.online_kiosks??0);setText("updatedAt",`${state.language==="hi"?"à¤…à¤ªà¤¡à¥‡à¤Ÿ":"Updated"} ${dateTime(data.generated_at)}`);
  const rows=data.job_status_breakdown||[],max=Math.max(1,...rows.map(r=>Number(r.count||0)));
  $("statusBreakdown").innerHTML=rows.length?rows.map(row=>`<div><div class="status-row-top"><span>${esc(row.status)}</span><strong>${Number(row.count||0)}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,Number(row.count||0)/max*100)}%"></div></div></div>`).join(""):`<p class="muted">No job status data yet.</p>`;
  const jobs=data.recent_jobs||[];$("recentJobs").innerHTML=jobs.length?jobs.map(job=>`<tr><td><span class="job-id" title="${esc(job.job_id)}">${esc(job.job_id)}</span></td><td>${esc(dateTime(job.created_at))}</td><td>${esc(job.kiosk_name||"â€”")}</td><td>${Number(job.pages||0)}</td><td>${esc(money(job.amount))}</td><td><span class="badge-status ${statusClass(job.payment_status)}">${esc(job.payment_status||"â€”")}</span></td><td><span class="badge-status ${statusClass(job.status)}">${esc(job.status||"â€”")}</span></td></tr>`).join(""):`<tr><td colspan="7">No print jobs found.</td></tr>`;
}
async function loadAdmins(){
  if(state.me?.role!=="SUPER_ADMIN")return;
  $("adminsTable").innerHTML=`<tr><td colspan="4">${t("loadingAdmins")}</td></tr>`;$("adminsEmpty").hidden=true;
  try{state.admins=await api("/admin/management/admins");renderAdmins();setText("adminNavCount",state.admins.length);}
  catch(err){setError(err.message);$("adminsTable").innerHTML=`<tr><td colspan="4">${esc(err.message)}</td></tr>`;}
}
function renderAdmins(){
  if(!$("adminsTable"))return;const q=($("adminSearch")?.value||"").trim().toLowerCase();
  const rows=state.admins.filter(a=>`${a.name||""} ${a.email||""} ${a.role||""}`.toLowerCase().includes(q));
  $("adminsTable").innerHTML=rows.map(a=>`<tr><td><div class="table-person"><span class="avatar">${esc(initials(a.name))}</span><strong>${esc(a.name||"â€”")}</strong></div></td><td>${esc(a.email||"â€”")}</td><td><span class="badge-status">${esc(a.role||"REGULAR_ADMIN")}</span></td><td><span class="badge-status ${a.is_active?"active":"inactive"}">${a.is_active?t("active"):t("inactive")}</span></td></tr>`).join("");
  $("adminsEmpty").hidden=rows.length!==0;
  if(rows.length===0)$("adminsEmpty").querySelector("p").textContent=q?t("noSearchResults"):t("noAdminsCaption");
  populateAssignmentOptions();
}
async function createAdmin(e){
  e.preventDefault();const b=$("saveAdminButton"),err=$("adminFormError");err.textContent="";
  const payload={name:$("newAdminName").value.trim(),email:$("newAdminEmail").value.trim().toLowerCase(),password:$("newAdminPassword").value};
  if(payload.password.length<8){err.textContent="Password must contain at least 8 characters.";return;}
  b.disabled=true;
  try{await api("/admin/management/admins",{method:"POST",body:JSON.stringify(payload)});closeDialog("adminDialog");$("adminCreateForm").reset();showToast(t("createSuccess"));await loadAdmins();}
  catch(ex){err.textContent=ex.message;}
  finally{b.disabled=false;}
}
async function createKiosk(e){
  e.preventDefault();

  if(state.me?.role!=="SUPER_ADMIN"){
    $("kioskFormError").textContent="Super Admin access is required.";
    return;
  }

  const button=$("saveKioskButton");
  const error=$("kioskFormError");
  error.textContent="";

  const kioskId=$("newKioskId").value.trim();
  const name=$("newKioskName").value.trim();
  const locationValue=$("newKioskLocation").value.trim();

  if(!kioskId || !name){
    error.textContent="Kiosk ID and kiosk name are required.";
    return;
  }

  const params=new URLSearchParams({kiosk_id:kioskId,name});
  if(locationValue)params.set("location",locationValue);

  button.disabled=true;

  try{
    const result=await api(`/kiosk/register?${params.toString()}`,{method:"POST"});

    if(!result.kiosk_secret){
      throw new Error("Kiosk registered, but the API did not return a secret. Check the backend response before retrying.");
    }

    $("kioskFields").hidden=true;
    $("kioskSecretResult").hidden=false;
    $("kioskSecretValue").value=result.kiosk_secret;
    button.hidden=true;

    $("kioskCreateForm").querySelector('[data-close="kioskDialog"]').textContent="Done";
    showToast("Kiosk registered successfully.");
    await loadKiosks();
  }catch(ex){
    error.textContent=ex.message||"Unable to register kiosk.";
  }finally{
    button.disabled=false;
  }
}
async function loadKiosks(){
  if(state.me?.role!=="SUPER_ADMIN")return;
  $("kioskGrid").innerHTML=`<div class="loading-card"><span class="spinner"></span><span>${t("loadingKiosks")}</span></div>`;$("kiosksEmpty").hidden=true;
  try{state.kiosks=await api("/admin/management/kiosks");renderKiosks();}
  catch(err){setError(err.message);$("kioskGrid").innerHTML=`<div class="panel">${esc(err.message)}</div>`;}
}
function renderKiosks(){
  if(!$("kioskGrid"))return;const q=($("kioskSearch")?.value||"").trim().toLowerCase();
  const rows=state.kiosks.filter(k=>`${k.name||""} ${k.kiosk_id||""} ${k.location||""} ${k.id||""}`.toLowerCase().includes(q));
  $("kioskGrid").innerHTML=rows.map(k=>`<article class="kiosk-card"><div class="kiosk-card-top"><span class="kiosk-device-icon">â–£</span><div style="min-width:0"><h3>${esc(k.name||"PayPrint kiosk")}</h3><span class="kiosk-code">Public code Â· ${esc(k.kiosk_id||"â€”")}</span></div><span class="badge-status ${k.is_active?"active":"inactive"}">${k.is_active?t("active"):t("inactive")}</span></div><div class="kiosk-meta"><div><span>Internal database ID</span><strong>${esc(k.id)}</strong></div><div><span>Location</span><strong>${esc(k.location||"â€”")}</strong></div><div><span>Last seen</span><strong>${esc(dateTime(k.last_seen))}</strong></div></div></article>`).join("");
  $("kiosksEmpty").hidden=rows.length!==0;
  if(rows.length===0)$("kiosksEmpty").querySelector("p").textContent=q?t("noSearchResults"):t("noKiosksCaption");
  populateAssignmentOptions();
}
async function loadAssignments(){
  if(state.me?.role!=="SUPER_ADMIN")return;
  $("assignmentsTable").innerHTML=`<tr><td colspan="4">${t("loadingAssignments")}</td></tr>`;$("assignmentsEmpty").hidden=true;
  try{state.assignments=await api("/admin/management/assignments");renderAssignments();}
  catch(err){setError(err.message);$("assignmentsTable").innerHTML=`<tr><td colspan="4">${esc(err.message)}</td></tr>`;}
}
function renderAssignments(){
  if(!$("assignmentsTable"))return;setText("assignmentCount",state.assignments.length);
  $("assignmentsTable").innerHTML=state.assignments.map(a=>`<tr><td><div class="table-person"><span class="avatar">${esc(initials(a.admin_name))}</span><div><strong>${esc(a.admin_name||"â€”")}</strong><small>${esc(a.admin_email||"")}</small></div></div></td><td>${esc(a.kiosk_name||"â€”")}</td><td><span class="badge-status">#${esc(a.kiosk_code||"â€”")}</span><small class="table-subline">DB ID: ${esc(a.kiosk_id)}</small></td><td><button class="text-danger" type="button" data-remove-assignment="${Number(a.id)}">${t("removeAssignmentAction")}</button></td></tr>`).join("");
  $("assignmentsEmpty").hidden=state.assignments.length!==0;
  $("assignmentsTable").querySelectorAll("[data-remove-assignment]").forEach(b=>b.addEventListener("click",()=>{state.pendingRemoval=Number(b.dataset.removeAssignment);$("confirmError").textContent="";openDialog("confirmDialog");}));
  populateAssignmentOptions();
}
function populateAssignmentOptions(){
  const adminSelect=$("assignmentAdmin"),kioskSelect=$("assignmentKiosk");if(!adminSelect||!kioskSelect)return;
  const previousAdmin=adminSelect.value,previousKiosk=kioskSelect.value;
  adminSelect.innerHTML=`<option value="">${state.language==="hi"?"à¤à¤¡à¤®à¤¿à¤¨ à¤šà¥à¤¨à¥‡à¤‚":"Select an admin"}</option>`+state.admins.filter(a=>a.is_active&&["ADMIN","REGULAR_ADMIN"].includes(a.role)).map(a=>`<option value="${Number(a.id)}">${esc(a.name)} Â· ${esc(a.email)}</option>`).join("");
  kioskSelect.innerHTML=`<option value="">${state.language==="hi"?"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤šà¥à¤¨à¥‡à¤‚":"Select a kiosk"}</option>`+state.kiosks.filter(k=>k.is_active).map(k=>`<option value="${Number(k.id)}">${esc(k.name||"Kiosk")} Â· Code ${esc(k.kiosk_id)} Â· DB ID ${Number(k.id)}</option>`).join("");
  if([...adminSelect.options].some(o=>o.value===previousAdmin))adminSelect.value=previousAdmin;
  if([...kioskSelect.options].some(o=>o.value===previousKiosk))kioskSelect.value=previousKiosk;
}
async function openAssignmentModal(){
  if(!state.admins.length)await loadAdmins();if(!state.kiosks.length)await loadKiosks();
  populateAssignmentOptions();$("assignmentFormError").textContent="";openDialog("assignmentDialog");
}
async function createAssignment(e){
  e.preventDefault();const b=$("saveAssignmentButton"),err=$("assignmentFormError");err.textContent="";
  const user_id=Number($("assignmentAdmin").value),kiosk_id=Number($("assignmentKiosk").value);
  if(!user_id||!kiosk_id){err.textContent="Select both an admin and a kiosk.";return;}
  b.disabled=true;
  try{await api("/admin/management/assignments",{method:"POST",body:JSON.stringify({user_id,kiosk_id})});closeDialog("assignmentDialog");showToast(t("assignSuccess"));await loadAssignments();}
  catch(ex){err.textContent=ex.message;}
  finally{b.disabled=false;}
}
async function removeAssignment(e){
  e.preventDefault();if(!state.pendingRemoval)return;const b=$("confirmRemoveButton");b.disabled=true;$("confirmError").textContent="";
  try{await api(`/admin/management/assignments/${state.pendingRemoval}`,{method:"DELETE"});closeDialog("confirmDialog");showToast(t("removeSuccess"));state.pendingRemoval=null;await loadAssignments();}
  catch(ex){$("confirmError").textContent=ex.message;}
  finally{b.disabled=false;}
}
function summaryText(){
  if(state.me?.role!=="SUPER_ADMIN")return t("adminScope");
  const m=state.overview?.metrics||{};
  return `${t("totalJobs")}: ${m.total_jobs??0}. ${t("paidRevenue")}: ${money(m.total_revenue_inr)}. ${t("totalKiosks")}: ${m.total_kiosks??0}. ${t("pending")}: ${m.pending_jobs??0}. ${t("completed")}: ${m.completed_jobs??0}.`;
}
function speak(text){
  if(!("speechSynthesis" in window)){showToast("Speech output is not supported in this browser.","error");return;}
  window.speechSynthesis.cancel();const utterance=new SpeechSynthesisUtterance(text);
  utterance.lang=state.language==="hi"?"hi-IN":"en-IN";utterance.rate=.93;window.speechSynthesis.speak(utterance);
}
function openVoice(){const p=$("voicePanel");p.hidden=false;setText("voiceStatus",t("voiceReady"));setText("voiceMessage",t("voiceIntro"));}
function handleVoiceCommand(command){
  const c=command.toLowerCase();
  if(c.includes("admin")){setView("admins");speak(state.language==="hi"?"à¤à¤¡à¤®à¤¿à¤¨ à¤ªà¥‡à¤œ à¤–à¥‹à¤²à¤¾ à¤—à¤¯à¤¾":"Opening admins.");return;}
  if(c.includes("kiosk")){setView("kiosks");speak(state.language==="hi"?"à¤•à¤¿à¤¯à¥‹à¤¸à¥à¤• à¤ªà¥‡à¤œ à¤–à¥‹à¤²à¤¾ à¤—à¤¯à¤¾":"Opening kiosks.");return;}
  if(c.includes("assignment")||c.includes("assign")){setView("assignments");speak(state.language==="hi"?"à¤…à¤¸à¤¾à¤‡à¤¨à¤®à¥‡à¤‚à¤Ÿ à¤ªà¥‡à¤œ à¤–à¥‹à¤²à¤¾ à¤—à¤¯à¤¾":"Opening assignments.");return;}
  if(c.includes("overview")||c.includes("dashboard")||c.includes("home")){setView("overview");speak(state.language==="hi"?"à¤“à¤µà¤°à¤µà¥à¤¯à¥‚ à¤–à¥‹à¤²à¤¾ à¤—à¤¯à¤¾":"Opening overview.");return;}
  if(c.includes("summary")||c.includes("report")||c.includes("à¤¸à¤¾à¤°à¤¾à¤‚à¤¶")){speak(summaryText());return;}
  setText("voiceMessage",t("unknownVoice"));speak(t("unknownVoice"));
}
function startListening(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){setText("voiceStatus",t("voiceUnsupported"));setText("voiceMessage",t("voiceUnsupported"));return;}
  if(state.voiceRecognition){try{state.voiceRecognition.stop();}catch(_){}state.voiceRecognition=null;}
  const rec=new SR();state.voiceRecognition=rec;rec.lang=state.language==="hi"?"hi-IN":"en-IN";rec.interimResults=false;rec.maxAlternatives=1;
  $("voicePanel").classList.add("listening");setText("voiceStatus",t("voiceListening"));setText("voiceMessage",t("voicePermission"));
  rec.onresult=e=>{const command=e.results[0][0].transcript;setText("voiceMessage",`â€œ${command}â€`);handleVoiceCommand(command);};
  rec.onerror=e=>{setText("voiceStatus",e.error==="not-allowed"?"Microphone permission denied":t("voiceUnsupported"));$("voicePanel").classList.remove("listening");};
  rec.onend=()=>{$("voicePanel").classList.remove("listening");if($("voiceStatus").textContent===t("voiceListening"))setText("voiceStatus",t("voiceReady"));state.voiceRecognition=null;};
  try{rec.start();}catch(_){setText("voiceStatus",t("voiceUnsupported"));$("voicePanel").classList.remove("listening");}
}
function closeMobileMenu(){$("sidebar")?.classList.remove("open");$("mobileScrim")?.classList.remove("show");}
function bindDashboard(){
  document.querySelectorAll(".nav-link[data-view]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.view)));
  $("refreshButton")?.addEventListener("click",()=>state.view==="overview"?loadOverview():state.view==="admins"?loadAdmins():state.view==="kiosks"?loadKiosks():loadAssignments());
  $("logoutButton")?.addEventListener("click",()=>{if("speechSynthesis"in window)window.speechSynthesis.cancel();clearSession();location.replace("login.html");});
  $("langButton")?.addEventListener("click",switchLanguage);$("addAdminButton")?.addEventListener("click",()=>{$("adminFormError").textContent="";openDialog("adminDialog");});
  $("addKioskButton")?.addEventListener("click",()=>{
    $("kioskCreateForm").reset();
    $("kioskFormError").textContent="";
    $("kioskFields").hidden=false;
    $("kioskSecretResult").hidden=true;
    $("kioskSecretValue").value="";
    $("saveKioskButton").hidden=false;
    $("saveKioskButton").disabled=false;
    $("kioskCreateForm").querySelector('[data-close="kioskDialog"]').textContent="Close";
    openDialog("kioskDialog");
  });
  $("kioskCreateForm")?.addEventListener("submit",createKiosk);
  $("copyKioskSecret")?.addEventListener("click",async()=>{
    const secret=$("kioskSecretValue").value;
    try{
      await navigator.clipboard.writeText(secret);
      showToast("Kiosk secret copied.");
    }catch(_){
      $("kioskSecretValue").focus();
      $("kioskSecretValue").select();
      showToast("Secret selected. Copy it manually.");
    }
  });
  $("addAssignmentButton")?.addEventListener("click",openAssignmentModal);$("adminCreateForm")?.addEventListener("submit",createAdmin);$("assignmentForm")?.addEventListener("submit",createAssignment);$("confirmForm")?.addEventListener("submit",removeAssignment);
  $("reloadAdmins")?.addEventListener("click",loadAdmins);$("reloadKiosks")?.addEventListener("click",loadKiosks);
  $("adminSearch")?.addEventListener("input",renderAdmins);$("kioskSearch")?.addEventListener("input",renderKiosks);
  $("voiceButton")?.addEventListener("click",openVoice);$("helpSpeak")?.addEventListener("click",()=>{openVoice();speak(t("voiceIntro"));});
  $("closeVoice")?.addEventListener("click",()=>{$("voicePanel").hidden=true;if(state.voiceRecognition)try{state.voiceRecognition.stop();}catch(_){}});
  $("speakSummary")?.addEventListener("click",()=>speak(summaryText()));$("listenCommand")?.addEventListener("click",startListening);
  $("mobileMenu")?.addEventListener("click",()=>{$("sidebar").classList.add("open");$("mobileScrim").classList.add("show");});$("mobileScrim")?.addEventListener("click",closeMobileMenu);
  bindCloseButtons();
  document.querySelectorAll("dialog").forEach(d=>d.addEventListener("click",e=>{if(e.target===d)closeDialog(d.id);}));
}
document.addEventListener("DOMContentLoaded",()=>{
  if($("loginForm"))initLogin();
  if($("view-overview")){bindDashboard();initDashboard();}
});

