# 📨 rackmail

**rackmail** is a Python-based CLI tool for managing and interacting with Rackspace Hosted Mailboxes. Built with simplicity and flexibility in mind, it streamlines common admin-related tasks from your terminal—perfect for sysadmins, devs, and automation pros.

## 🚀 Features

- 📤 Interact with emails
- 📜 Get info about emails  
- ⚙️ Easy setup with just 3 ENV Variables. 
- 🔌 Integrates cleanly into scripts and cron jobs

## 📦 Installation

```bash
pip install rackmail
```

Or install from source:

```bash
git clone https://github.com/yourusername/rackmail.git
cd rackmail
pip install -e .
```

## 🛠 Usage

```bash
rackmail --help
```

### Common Commands

```bash
rackmail enableuser -e user.name -d domain.com #Enables a users mailbox
rackmail disableuser -e user.name -d domain.com #Disables a users mailbox
```

## ⚙️ Configuration
You will need information from your Rackspace Hosted Email tenant to fully setup this tool. Since this tool uses the Rackspace API, you can find most of this information in the API Key's section of Rackspace's Admin console.

1. ```User Key```
2. ```Customer ID```
3. ```X-Api-Signature Header```

To get the correct X-API-Signature Header. Please use rackmailcli as the useragent header.

After you get the three items listed above, you need to setup the environment on your machine. Please use the following key value pairs in your environment. Replacing the values of each with the values you got from Rackspace's admin console.

1. ```RACKSPACE_API_KEY = User Key```
2. ```RACKSPACE_CUSTOMER_ID = Customer ID```
3. ```RACKSPACE_API_HEADER = X-Api-Signature Header```

## 🔧 Development

To Setup the code base.
```bash
git clone https://github.com/lilrebel17/rackmail.git
cd src
pip install -r requirements.txt
```

To install the project as a package for testing.
```bash
cd rackmail #Projects root directory
pip install . #Installs the project as a pip package.
```

To build a distributable
```bash
cd rackmail #Projects root directory
python -m build
```

## 🤝 Contributing

Issues and PRs welcome. Just follow the standard Python etiquette and maybe don’t name your test email “bombthis@company.com” (again).