# iam-user-manager

CLI tool for managing IAM users using YAML format template files.

## Requirements

- make
- pyenv

## Setup

```
make init
```

## How to use

### Update IAM users

Create a `users.yml` and write the user setting in it.

```
cp users.sample.yml users.yml
vi users.yml
```

Run the tool.

```
./iam_user_manager.py update users.yml
```

### Delete IAM users

TODO

