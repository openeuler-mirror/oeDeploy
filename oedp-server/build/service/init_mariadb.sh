# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-01-15
# ======================================================================================================================

is_silent_installation=$1
CONFIG_FILE="/etc/oedp-server/silent_installation.conf"

# 读取配置文件
function read_config_value {
    local key="$1"

    # 判断配置文件中 key 是否存在
    local item=$(grep "^${key} =" "$config_file")
    if [[ -z "${item}" ]]; then
        echo -e "\e[1;31mThe key '${key}' not found in the configuration file ${CONFIG_FILE}\e[0m"
        exit 1
    fi

    # 判断配置文件中对应 key 的值是否存在
    local value=$(echo "${item}" | awk -F= '{print $2}' | xargs)
    if [[ -n "${value}" ]]; then
        echo "${value}"
    else
        echo -e "\e[1;31mThe value of key '${key}' is empty in the configuration file ${CONFIG_FILE}\e[0m"
        exit 1
    fi
}

# 检查密码复杂度，密码至少包含8个字符,大小写字母、数字、特殊符号三种以上
function check_password_complexity()
{
  local variable_content=$1
  local complexity=0

  if [[ ${#variable_content} -ge 8 ]]; then
    complexity=$((${complexity}+1))
  else
    return 1
  fi

  if [[ "${variable_content}" =~ [[:upper:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ [[:lower:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ [[:digit:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ [[:punct:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  unset variable_content
  if [[ "${complexity}" -ge 4 ]]; then
    return 0
  else
    return 1
  fi
}


# 检查自定义数据库名字复杂度，自定义数据库名字至少包含2个字符,大小写字母、下划线、数字两种以上
function check_database_name()
{
  local variable_content=$1
  local complexity=0

  if [[ "${variable_content}" =~ [[:upper:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ [[:lower:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ [[:digit:]] ]]; then
    complexity=$((${complexity}+1))
  fi

  if [[ "${variable_content}" =~ "_" ]]; then
    complexity=$((${complexity}+1))
  fi
  # 包含 a-zA-Z0-9_ 之外的字符都不符合要求
  if [[ "${variable_content}" =~ [^a-zA-Z0-9_] ]]; then
    complexity=0
  fi

  unset variable_content
  if [[ ${complexity} -ge 2 ]]; then
    return 0
  else
    return 1
  fi
}


echo -e "\e[1;34mStart to configure MariaDB for oeDploy WebServer.\e[0m"
while true
do
  # 交互式安装会询问 MariaDB 是否已配置，静默安装默认没有被配置
  if [ "${is_silent_installation}" == "false" ]; then
    read -p "Whether MariaDB is configured? [Y/n] (default: n) " Y_N
  else
    Y_N="n"
  fi
  # 判断 MariaDB 是否已配置，若已配置则跳过，若没有则开始配置
  if [[ "${Y_N}" == "y" || "${Y_N}" == "Y" ]]; then
    break
  elif [[ ! -n "${Y_N}" || "${Y_N}" == "N" || "${Y_N}" == "n" ]]; then
    # 启动 MariaDB 服务
    systemctl start mariadb
    if [[ $? -ne 0 ]]; then
      echo -e "\e[1;31mThe MariaDB service fails to start.\e[0m"
      exit 1
    fi
    # 检查服务是否启动
    mariadb_status=$(systemctl is-active mariadb)
    if [[ "${mariadb_status}" == "active" ]]; then
      echo -e "\e[1;32mThe MariaDB service is active.\e[0m"
    else
      echo -e "\e[1;31mThe MariaDB service is inactive.\e[0m"
      exit 1
    fi
    # 设置为开机自启动服务
    systemctl enable mariadb

    # 初始化数据库
    if [ "${is_silent_installation}" == "false" ]; then
      mysql_secure_installation
    else
      default_root_pw="\n"
      set_root_pw="y"
      root_password=$(read_config_value "root_password")
      change_root_pw="n"
      remove_anonymous_users="y"
      disallow_root_login_remotely="n"
      remove_test_database_and_access_to_it="y"
      reload_privilege_tables="y"
      # 首次安装，mariadb 的 root 密码为空，需要设置 root 密码
      input_string="${default_root_pw}"
      input_string+="${set_root_pw}\n"
      input_string+="${root_password}\n"
      input_string+="${root_password}\n"
      input_string+="${remove_anonymous_users}\n"
      input_string+="${disallow_root_login_remotely}\n"
      input_string+="${remove_test_database_and_access_to_it}\n"
      input_string+="${reload_privilege_tables}\n"
      expect -c "
set timeout 5
spawn mysql_secure_installation
expect \"Enter current password for root (enter for none):\"
send \"${input_string}\"
expect {
  \"*Access denied*\" {
    exit 1
  }
  eof
}
"
      return_code=$?
      if [[ "${return_code}" == "1" ]]; then
        # 非首次安装，mariadb 的 root 密码已设置
        input_string="${root_password}\n"
        input_string+="${change_root_pw}\n"
        input_string+="${remove_anonymous_users}\n"
        input_string+="${disallow_root_login_remotely}\n"
        input_string+="${remove_test_database_and_access_to_it}\n"
        input_string+="${reload_privilege_tables}\n"
        expect -c "
set timeout 5
spawn mysql_secure_installation
expect \"Enter current password for root (enter for none):\"
send \"${input_string}\"
expect {
  \"*Access denied*\" {
    puts \"Error: Incorrect mariadb root password. Please change the value of root_password in the ${CONFIG_FILE}\"
    exit 1
  }
  eof
}
"
        if [[ "$?" == "1" ]]; then
          exit 1
        fi
      fi
    fi
    echo ""
    break
  else
    echo -e "\e[1;31mThe input is invalid. Please input again.\e[0m"
  fi
done

unset Y_N

# 检查防火墙是否启动，如果启动则检查 3306 端口是否在防火墙白名单中，如果不存在则添加到白名单中
status=$(systemctl status firewalld | grep -E "Active" | awk -F":" '{print $2}'| awk -F" " '{print $1}')
if [[ "${status}" == "active" ]]; then
  port_3306=$(firewall-cmd --query-port=3306/tcp)
  if [[ "${port_3306}" == "no" ]]; then
    port_3306=$(firewall-cmd --zone=public --add-port=3306/tcp --permanent)
    firewall-cmd --reload
  fi
  port_3306=$(firewall-cmd --query-port=3306/tcp)
  if [[ "${port_3306}" != "yes" ]]; then
    echo -e "\e[1;31mFailed to enable port 3306.\e[0m"
    exit 1
  fi
fi

# 输入或获取 oedp 密码
stty -echo
if [ "${is_silent_installation}" == "false" ]; then
  should_break=false
  for i in {1..5}; do
    read -p "Enter the password of oedp user for MariaDB: " oedp_passwd_01
    echo ""
    read -p "Confirm: " oedp_passwd_02
    if [[ "${oedp_passwd_01}" == "${oedp_passwd_02}" ]]; then
      should_break=true
      break
    fi
    echo -e "\e[1;33mThe provided passwords do not match. Please re-enter them for verification. \e[0m"
  done
  if [ ! ${should_break} ]; then
    exit 1
  fi
  oedp_passwd=${oedp_passwd_01}
else
  oedp_passwd=$(read_config_value "oedp_password")
fi
stty echo
echo ""

# 检查 oedp 用户密码的复杂度
while true
do
  check_password_complexity ${oedp_passwd}
  if [[ $? -ne 0 ]]; then
    stty -echo
    if [ "${is_silent_installation}" == "false" ]; then
      echo -e "\e[1;34mThe password must contain at least eight characters, including uppercase lowercase digits and special characters.\e[0m"
      echo -e "\e[1;31mThe password of the oedp user for MariaDB is invalid. Please input again.\e[0m"
      should_break=false
      for i in {1..5}; do
        read -p "Enter the password of oedp user for MariaDB: " oedp_passwd_01
        echo ""
        read -p "Confirm: " oedp_passwd_02
        if [[ "${oedp_passwd_01}" == "${oedp_passwd_02}" ]]; then
          should_break=true
          break
        fi
        echo -e "\e[1;33mThe provided passwords do not match. Please re-enter them for verification. \e[0m"
      done
      if [ ! ${should_break} ]; then
        exit 1
      fi
      oedp_passwd=${oedp_passwd_01}
    else
      echo -e "\e[1;34mThe password must contain at least eight characters, including uppercase lowercase digits and special characters.\e[0m"
      echo -e "\e[1;31mThe password of the oedp user for MariaDB is invalid. Please change the value of oedp_password in the ${CONFIG_FILE}.\e[0m"
      stty echo
      exit 1
    fi
    stty echo
    echo ""
  else
    break
  fi
done

# 获取自定义数据库名
while true
do
  echo -e "\e[1;34mIf the selected database already exists, it will be overwritten.\e[0m"
  if [ "${is_silent_installation}" == "false" ]; then
    read -p "Use default oedp_db database? [Y/n] (default: Y) " Y_N
  else
    Y_N="Y"
  fi
  # 使用默认
  if [[ ! -n "${Y_N}" || "${Y_N}" == "y" || "${Y_N}" == "Y" ]]; then
    mariadb_name=oedp_db
    break
  elif [[ "${Y_N}" == "N" || "${Y_N}" == "n" ]]; then
    # 用户自定义数据库
    read -p "Please input the name of the database to be created: " mariadb_name
    check_database_name ${mariadb_name}
    if [[ $? -ne 0 ]]; then
      echo -e "\e[1;34mThe database name must contain at least two types of characters, including uppercase lowercase underscores and digits.\e[0m"
      echo -e "\e[1;31mThe input database name entered is invalid. Please input again.\e[0m"
    else
      break
    fi
  else
    echo -e "\e[1;31mThe input is invalid. Please input again.\e[0m"
  fi
done
unset Y_N

# 创建用户名为 oedp 的数据库
stty -echo
if [ "${is_silent_installation}" == "false" ]; then
  read -p "Enter the password of the root user of the MariaDB again: " root_password
else
  root_password=$(read_config_value "root_password")
fi
stty echo
mysql -uroot -p${root_password} << EOF
DROP DATABASE IF EXISTS ${mariadb_name};
CREATE DATABASE IF NOT EXISTS ${mariadb_name} CHARACTER SET utf8 COLLATE utf8_bin;

DELETE FROM mysql.user WHERE User='oedp';
DELETE FROM mysql.db WHERE User='oedp';
flush privileges;
# oedp 用户权限仅限操作自定义新创建的数据库
CREATE USER 'oedp'@'localhost' IDENTIFIED BY '${mariadb_passwd}';
GRANT ALL ON ${mariadb_name}.* TO 'oedp'@'localhost' IDENTIFIED BY '${mariadb_passwd}' WITH GRANT OPTION;
flush privileges;
EOF

unset root_password

if [[ $? -ne 0 ]]; then
  echo -e "\e[1;31mMariaDB configurations are incorrect. Please check the MariaDB root password or the status of MariaDB.\e[0m"
  exit 1
fi

echo -e "\e[1;32mMariaDB is configured successfully.\e[0m"