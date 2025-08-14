-- =============================================
-- 脚本名称: init.sql
-- 版本号: 0.0.1
-- 描述: 数据库初始化脚本
-- 创建时间: 2025-04-28
-- 作者: amiko
-- 修改历史:
--   2025-04-28 初始版本
-- =============================================

-- 获取数据库名称
-- SET @db_name = IFNULL(@db_name, 'magic_ai_box');

-- 创建数据库
-- CREATE DATABASE IF NOT EXISTS `magic_ai_box` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
-- USE `magic_ai_box`;


-- 清空所有tables
SET FOREIGN_KEY_CHECKS = 0;
    
SELECT CONCAT('DROP TABLE IF EXISTS ', GROUP_CONCAT(table_name SEPARATOR ', '), ';')
INTO @drop_tables
FROM information_schema.tables 
WHERE table_schema = DATABASE();

-- 检查@drop_tables是否为空
SET @sql = IF(@drop_tables IS NOT NULL, @drop_tables, 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
    
SET FOREIGN_KEY_CHECKS = 1;

-- 创建用户表[表名: sys_users]
CREATE TABLE IF NOT EXISTS sys_users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（唯一）',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    full_name VARCHAR(100) DEFAULT NULL COMMENT '用户全名',
    wechat_openid VARCHAR(100) DEFAULT NULL COMMENT '微信小程序openid',
    wechat_unionid VARCHAR(100) DEFAULT NULL COMMENT '微信unionid',
    wechat_nickname VARCHAR(100) DEFAULT NULL COMMENT '微信昵称',
    avatar_url VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    wechat_bound BOOLEAN DEFAULT FALSE COMMENT '是否绑定微信',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密后的密码（推荐Bcrypt）',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户是否激活',
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建角色表[表名: sys_roles]
CREATE TABLE IF NOT EXISTS sys_roles (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名（唯一）',
  is_active BOOLEAN DEFAULT TRUE COMMENT '角色是否启用',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '角色描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';


-- 创建用户角色关联表[表名: sys_user_roles]
CREATE TABLE IF NOT EXISTS sys_user_roles (
  user_id BIGINT NOT NULL COMMENT '用户ID',
  role_id BIGINT NOT NULL COMMENT '角色ID',
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES sys_roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';


-- 创建权限表[表名: sys_permissions]
CREATE TABLE IF NOT EXISTS sys_permissions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '权限名称（如：用户管理）',
  code VARCHAR(100) NOT NULL UNIQUE COMMENT '权限唯一标识（如：user:create）',
  icon VARCHAR(100) DEFAULT NULL COMMENT '权限图标',
  type ENUM('MENU','PAGE', 'BUTTON', 'API') NOT NULL COMMENT '权限类型',
  parent_id BIGINT DEFAULT NULL COMMENT '父权限ID（用于树形结构）',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  path VARCHAR(255) DEFAULT NULL COMMENT '菜单或路由路径（前端用）',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '权限描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES sys_permissions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';


-- 创建角色权限关联表[表名: sys_role_permissions]
CREATE TABLE IF NOT EXISTS sys_role_permissions (
  role_id BIGINT NOT NULL,
  permission_id BIGINT NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES sys_roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES sys_permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';


-- 创建应用表[表名: sys_apps]
CREATE TABLE IF NOT EXISTS sys_apps (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL COMMENT '应用名称',
  platform ENUM('WEB', 'ANDROID', 'IOS', 'MINIAPP') NOT NULL COMMENT '应用平台',
  app_key VARCHAR(64) NOT NULL UNIQUE COMMENT '应用唯一标识（最多64位）',
  app_type ENUM('FREE', 'PAID') NOT NULL DEFAULT 'FREE' COMMENT '应用类型：免费/付费',
  status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE' COMMENT '应用状态',
  creator_id BIGINT DEFAULT NULL COMMENT '创建者用户ID',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '应用描述',
  domain_whitelist JSON DEFAULT NULL COMMENT '域名白名单',
  ip_whitelist JSON DEFAULT NULL COMMENT 'IP白名单',
  rate_limit_per_minute INT DEFAULT 1000 COMMENT '每分钟调用限制',
  rate_limit_per_day INT DEFAULT 10000 COMMENT '每日调用限制',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (creator_id) REFERENCES sys_users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用表';

-- 应用场景表[表名: sys_app_scenarios]
CREATE TABLE IF NOT EXISTS sys_app_scenarios (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '场景名称',
  code VARCHAR(50) NOT NULL UNIQUE COMMENT '场景代码',
  description VARCHAR(255) DEFAULT NULL COMMENT '场景描述',
  scenario_type ENUM('OCR', 'AI_VISION', 'NLP', 'ASR', 'ANALYTICS') DEFAULT 'OCR' COMMENT '场景类型',
  points_cost INT DEFAULT 0 COMMENT '积分消耗（免费模式）',
  daily_limit INT DEFAULT 0 COMMENT '每日调用限制（0为无限制）',
  monthly_limit INT DEFAULT 0 COMMENT '每月调用限制（0为无限制）',
  status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE' COMMENT '场景状态',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用场景表';

-- 场景API关联表[表名: sys_scenario_apis]
CREATE TABLE IF NOT EXISTS sys_scenario_apis (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  scenario_id BIGINT NOT NULL COMMENT '场景ID',
  api_path VARCHAR(255) NOT NULL COMMENT 'API路径',
  api_method ENUM('GET', 'POST', 'PUT', 'DELETE', 'PATCH') NOT NULL COMMENT 'HTTP方法',
  api_name VARCHAR(100) NOT NULL COMMENT 'API名称',
  api_description VARCHAR(255) DEFAULT NULL COMMENT 'API描述',
  is_required BOOLEAN DEFAULT TRUE COMMENT '是否必需API',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scenario_id) REFERENCES sys_app_scenarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='场景API关联表';

-- 应用场景关联表[表名: sys_app_scenario_relations]
CREATE TABLE IF NOT EXISTS sys_app_scenario_relations (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT NOT NULL COMMENT '应用ID',
  scenario_id BIGINT NOT NULL COMMENT '场景ID',
  is_enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  custom_points_cost INT DEFAULT NULL COMMENT '自定义积分消耗（覆盖默认值）',
  quota_limit INT DEFAULT NULL COMMENT '配额限制',
  custom_monthly_limit INT DEFAULT NULL COMMENT '自定义每月限制',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  FOREIGN KEY (scenario_id) REFERENCES sys_app_scenarios(id) ON DELETE CASCADE,
  UNIQUE KEY uk_app_scenario (app_id, scenario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用场景关联表';

-- FTP配置信息表[表名: sys_ftp_configs]
CREATE TABLE IF NOT EXISTS sys_ftp_configs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT NOT NULL COMMENT '应用ID',
  host VARCHAR(100) NOT NULL COMMENT 'FTP主机',
  port INT NOT NULL COMMENT 'FTP端口',
  username VARCHAR(100) NOT NULL COMMENT 'FTP用户名',
  password VARCHAR(100) NOT NULL COMMENT 'FTP密码',
  is_active BOOLEAN DEFAULT TRUE COMMENT '配置是否启用',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '配置描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FTP配置信息表';


-- 创建api-access-key 表[表名: sys_access_keys]
CREATE TABLE IF NOT EXISTS sys_access_keys (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT NOT NULL COMMENT '应用ID',
  access_key VARCHAR(100) NOT NULL UNIQUE COMMENT 'API访问密钥',
  is_active BOOLEAN DEFAULT TRUE COMMENT '密钥是否启用',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '密钥描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API访问密钥表';

--  创建工具服务信息表[表名: sys_tools]
CREATE TABLE IF NOT EXISTS sys_tools (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '工具/服务名称',
  icon VARCHAR(100) DEFAULT NULL COMMENT '工具图标',
  type ENUM('API', 'PLUGIN') NOT NULL COMMENT '工具类型',
  app_key VARCHAR(100) NOT NULL COMMENT '应用唯一标识',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '工具描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工具服务信息表';

-- 积分计划表[表名: sys_points_plans]
CREATE TABLE IF NOT EXISTS sys_points_plans (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT NOT NULL COMMENT '应用ID',
  name VARCHAR(50) NOT NULL COMMENT '积分计划名称',
  description VARCHAR(255) DEFAULT NULL COMMENT '计划描述',
  signup_bonus INT DEFAULT 100 COMMENT '注册奖励积分',
  daily_signin_base INT DEFAULT 10 COMMENT '每日签到基础积分',
  daily_signin_max INT DEFAULT 50 COMMENT '连续签到最大积分',
  share_bonus INT DEFAULT 20 COMMENT '分享奖励积分',
  invite_bonus INT DEFAULT 100 COMMENT '邀请奖励积分',
  points_expire_days INT DEFAULT 365 COMMENT '积分有效期（天）',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分计划表';

-- 用户积分记录表[表名: sys_user_points]
CREATE TABLE IF NOT EXISTS sys_user_points (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  app_id BIGINT NOT NULL COMMENT '应用ID',
  current_points INT DEFAULT 0 COMMENT '当前积分余额',
  total_earned INT DEFAULT 0 COMMENT '累计获得积分',
  total_consumed INT DEFAULT 0 COMMENT '累计消耗积分',
  last_signin_date DATE DEFAULT NULL COMMENT '最后签到日期',
  continuous_signin_days INT DEFAULT 0 COMMENT '连续签到天数',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  UNIQUE KEY uk_user_app_points (user_id, app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户积分记录表';

-- 积分变动记录表[表名: sys_points_transactions]
CREATE TABLE IF NOT EXISTS sys_points_transactions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  app_id BIGINT NOT NULL COMMENT '应用ID',
  transaction_type ENUM('EARN', 'CONSUME', 'EXPIRE', 'TRANSFER') NOT NULL COMMENT '交易类型',
  points_amount INT NOT NULL COMMENT '积分数量（正数为获得，负数为消耗）',
  source_type ENUM('SIGNUP', 'SIGNIN', 'SHARE', 'INVITE', 'TASK', 'PURCHASE', 'SCENARIO_CALL', 'ADMIN', 'EXPIRE', 'TRANSFER') NOT NULL COMMENT '来源类型',
  source_id BIGINT DEFAULT NULL COMMENT '来源ID（如场景ID、任务ID等）',
  description VARCHAR(255) DEFAULT NULL COMMENT '描述',
  balance_after INT NOT NULL COMMENT '交易后余额',
  expire_date DATE DEFAULT NULL COMMENT '积分过期日期',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分变动记录表';

-- 订阅计划信息表[表名: sys_subscription_plans]
CREATE TABLE IF NOT EXISTS sys_subscription_plans (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT DEFAULT NULL COMMENT '应用ID（NULL表示通用计划）',
  name VARCHAR(50) NOT NULL COMMENT '计划名称',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '计划描述',
  price DECIMAL(10, 2) NOT NULL COMMENT '计划价格',
  billing_cycle ENUM('MONTHLY', 'QUARTERLY', 'YEARLY') DEFAULT 'MONTHLY' COMMENT '计费周期',
  trial_days INT DEFAULT 0 COMMENT '试用天数',
  is_active BOOLEAN DEFAULT TRUE COMMENT '计划是否启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅计划信息表';

-- 订阅计划场景关联表[表名: sys_subscription_plan_scenarios]
CREATE TABLE IF NOT EXISTS sys_subscription_plan_scenarios (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  plan_id BIGINT NOT NULL COMMENT '订阅计划ID',
  scenario_id BIGINT NOT NULL COMMENT '场景ID',
  quota_limit INT DEFAULT 0 COMMENT '配额限制（0为无限制）',
  is_included BOOLEAN DEFAULT TRUE COMMENT '是否包含在计划中',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (plan_id) REFERENCES sys_subscription_plans(id) ON DELETE CASCADE,
  FOREIGN KEY (scenario_id) REFERENCES sys_app_scenarios(id) ON DELETE CASCADE,
  UNIQUE KEY uk_plan_scenario (plan_id, scenario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅计划场景关联表';

-- 应用订阅关联表[表名: sys_app_subscriptions]
CREATE TABLE IF NOT EXISTS sys_app_subscriptions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  app_id BIGINT NOT NULL COMMENT '应用ID',
  plan_id BIGINT DEFAULT NULL COMMENT '订阅计划ID（NULL表示免费应用）',
  subscription_type ENUM('FREE', 'PAID') DEFAULT 'FREE' COMMENT '订阅类型',
  status ENUM('ACTIVE', 'EXPIRED', 'CANCELLED', 'TRIAL') DEFAULT 'ACTIVE' COMMENT '订阅状态',
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '订阅开始时间',
  end_time TIMESTAMP NULL COMMENT '订阅结束时间',
  trial_end_time TIMESTAMP NULL COMMENT '试用结束时间',
  auto_renew BOOLEAN DEFAULT FALSE COMMENT '是否自动续费',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  FOREIGN KEY (plan_id) REFERENCES sys_subscription_plans(id) ON DELETE SET NULL,
  UNIQUE KEY uk_user_app_subscription (user_id, app_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用订阅关联表';

-- API调用日志表[表名: sys_api_call_logs]
CREATE TABLE IF NOT EXISTS sys_api_call_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT DEFAULT NULL COMMENT '应用ID',
  user_id BIGINT DEFAULT NULL COMMENT '用户ID',
  scenario_id BIGINT DEFAULT NULL COMMENT '场景ID',
  api_path VARCHAR(255) NOT NULL COMMENT 'API路径',
  http_method VARCHAR(10) NOT NULL COMMENT 'HTTP方法',
  call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
  response_time INT DEFAULT NULL COMMENT '响应时间（毫秒）',
  status_code INT DEFAULT NULL COMMENT 'HTTP状态码',
  call_result ENUM('SUCCESS', 'FAILED', 'ERROR') DEFAULT 'SUCCESS' COMMENT '调用结果',
  error_message TEXT DEFAULT NULL COMMENT '错误信息',
  request_size INT DEFAULT 0 COMMENT '请求大小（字节）',
  response_size INT DEFAULT 0 COMMENT '响应大小（字节）',
  ip_address VARCHAR(45) DEFAULT NULL COMMENT '客户端IP',
  user_agent TEXT DEFAULT NULL COMMENT '用户代理',
  points_consumed INT DEFAULT 0 COMMENT '消耗积分',
  quota_consumed INT DEFAULT 0 COMMENT '消耗配额',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE SET NULL,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE SET NULL,
  FOREIGN KEY (scenario_id) REFERENCES sys_app_scenarios(id) ON DELETE SET NULL,
  INDEX idx_app_call_time (app_id, call_time),
  INDEX idx_user_call_time (user_id, call_time),
  INDEX idx_scenario_call_time (scenario_id, call_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API调用日志表';

-- 订阅记录表[表名: sys_subscription_records]
CREATE TABLE IF NOT EXISTS sys_subscription_records (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  plan_id BIGINT NOT NULL COMMENT '订阅计划ID',
  app_subscription_id BIGINT DEFAULT NULL COMMENT '应用订阅ID',
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '订阅开始时间',
  end_time TIMESTAMP NULL COMMENT '订阅结束时间',
  status ENUM('ACTIVE', 'EXPIRED', 'CANCELED') DEFAULT 'ACTIVE' COMMENT '订阅状态',
  payment_status ENUM('UNPAID', 'PAID', 'REFUNDED') DEFAULT 'UNPAID' COMMENT '支付状态',
  payment_method ENUM('ALIPAY', 'WECHAT_PAY', 'BANK_TRANSFER') DEFAULT 'ALIPAY' COMMENT '支付方式',
  payment_time TIMESTAMP NULL COMMENT '支付时间',
  refund_time TIMESTAMP NULL COMMENT '退款时间',
  refund_reason VARCHAR(255) DEFAULT NULL COMMENT '退款原因',
  payment_amount DECIMAL(10, 2) DEFAULT NULL COMMENT '支付金额',
  refund_amount DECIMAL(10, 2) DEFAULT NULL COMMENT '退款金额',
  coupon_code VARCHAR(50) DEFAULT NULL COMMENT '优惠券编码',
  discount_amount DECIMAL(10, 2) DEFAULT NULL COMMENT '优惠金额',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (plan_id) REFERENCES sys_subscription_plans(id) ON DELETE CASCADE,
  FOREIGN KEY (app_subscription_id) REFERENCES sys_app_subscriptions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅记录表';


-- 订阅优惠券表[表名: sys_subscription_coupons]
CREATE TABLE IF NOT EXISTS sys_subscription_coupons (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  coupon_code VARCHAR(50) NOT NULL UNIQUE COMMENT '优惠券编码',
  discount_amount DECIMAL(10, 2) NOT NULL COMMENT '优惠金额',
  expiry_date DATE NOT NULL COMMENT '优惠券过期日期',
  is_active BOOLEAN DEFAULT TRUE COMMENT '优惠券是否启用',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '优惠券描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅优惠券表';

-- 优惠券使用记录表[表名: sys_subscription_coupon_usages]
CREATE TABLE IF NOT EXISTS sys_subscription_coupon_usages (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  coupon_id BIGINT NOT NULL COMMENT '优惠券ID',
  record_id BIGINT NOT NULL COMMENT '订阅记录ID',
  used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '使用时间',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (coupon_id) REFERENCES sys_subscription_coupons(id) ON DELETE CASCADE,
  FOREIGN KEY (record_id) REFERENCES sys_subscription_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='优惠券使用记录表';


-- 订阅计划额度关联表(一对多) [表名: sys_subscription_plan_quotas]
CREATE TABLE IF NOT EXISTS sys_subscription_plan_quotas (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  plan_id BIGINT NOT NULL COMMENT '计划ID',
  tool_id BIGINT NOT NULL COMMENT '工具ID',
  quota_type ENUM('API_CALLS', 'TOOLS_USAGE') NOT NULL COMMENT '额度类型',
  quota_value INT NOT NULL COMMENT '额度值',
  is_active BOOLEAN DEFAULT TRUE COMMENT '额度是否启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (plan_id) REFERENCES sys_subscription_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅计划额度关联表';


-- 订阅额度使用信息表[表名: sys_subscription_quota_usages]
CREATE TABLE IF NOT EXISTS sys_subscription_quota_usages (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  record_id BIGINT NOT NULL COMMENT '订阅记录ID',
  tool_id BIGINT NOT NULL COMMENT '工具ID',
  quota_type ENUM('API_CALLS', 'TOOLS_USAGE') NOT NULL COMMENT '额度类型',
  quota_used INT NOT NULL COMMENT '已使用额度',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (record_id) REFERENCES sys_subscription_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订阅额度使用信息表';


-- 附件表[表名: sys_attachments]
CREATE TABLE IF NOT EXISTS sys_attachments (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL COMMENT '附件名称',
  type VARCHAR(100) NOT NULL COMMENT '附件类型',
  size BIGINT NOT NULL COMMENT '附件大小',
  path VARCHAR(255) NOT NULL COMMENT '附件路径',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='附件表';

-- 附件管理表[表名: sys_annexes]
CREATE TABLE IF NOT EXISTS `sys_annexes` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '附件ID',
    `original_name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_name` VARCHAR(255) NOT NULL COMMENT '存储文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件路径',
    `file_key` VARCHAR(500) NOT NULL COMMENT '文件唯一标识',
    `file_size` BIGINT NOT NULL COMMENT '文件大小（字节）',
    `file_type` VARCHAR(100) NOT NULL COMMENT '文件类型',
    `mime_type` VARCHAR(100) COMMENT 'MIME类型',
    `file_extension` VARCHAR(20) COMMENT '文件扩展名',
    `storage_type` ENUM('QINIU', 'ALIYUN', 'TENCENT') NOT NULL DEFAULT 'QINIU' COMMENT '存储类型',
    `storage_path` VARCHAR(500) COMMENT '存储路径',
    `file_url` TEXT COMMENT '文件访问URL',
    `file_hash` VARCHAR(64) NOT NULL COMMENT '文件哈希值',
    `status` ENUM('UPLOADING', 'ACTIVE', 'DELETED', 'FAILED') NOT NULL DEFAULT 'UPLOADING' COMMENT '状态',
    `upload_user_id` BIGINT COMMENT '上传用户ID',
    `description` TEXT COMMENT '文件描述',
    `tags` TEXT COMMENT '文件标签(JSON格式)',
    `download_count` INT NOT NULL DEFAULT 0 COMMENT '下载次数',
    `is_public` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否公开',
    `expires_at` DATETIME COMMENT '过期时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX `idx_upload_user_id` (`upload_user_id`),
    INDEX `idx_file_hash` (`file_hash`),
    INDEX `idx_status` (`status`),
    INDEX `idx_storage_type` (`storage_type`),
    INDEX `idx_file_type` (`file_type`),
    INDEX `idx_is_public` (`is_public`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_file_key` (`file_key`),
    
    -- 外键约束
    FOREIGN KEY (`upload_user_id`) REFERENCES `sys_users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='附件管理表';


-- 备份信息表[表名: sys_backups]
CREATE TABLE IF NOT EXISTS sys_backups (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL COMMENT '备份名称',
  type ENUM('FULL', 'INCREMENTAL') NOT NULL COMMENT '备份类型',
  status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED') DEFAULT 'PENDING' COMMENT '备份状态',
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '备份开始时间',
  end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '备份结束时间',
  size BIGINT DEFAULT NULL COMMENT '备份大小',
  path VARCHAR(255) DEFAULT NULL COMMENT '备份路径',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备份信息表';

-- 备份附件关联表[表名: sys_backup_attachments]
CREATE TABLE IF NOT EXISTS sys_backup_attachments (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  backup_id BIGINT NOT NULL COMMENT '备份ID',
  attachment_id BIGINT NOT NULL COMMENT '附件ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (backup_id) REFERENCES sys_backups(id) ON DELETE CASCADE,
  FOREIGN KEY (attachment_id) REFERENCES sys_attachments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备份附件关联表';

-- 文章多级分类[表名: sys_article_categories]
CREATE TABLE IF NOT EXISTS sys_article_categories (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '分类名称',
  desc_info VARCHAR(255) DEFAULT NULL COMMENT '分类描述',
  parent_id BIGINT DEFAULT NULL COMMENT '父分类ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章多级分类';


-- 文章信息表[表名: sys_articles]
CREATE TABLE IF NOT EXISTS sys_articles (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL COMMENT '文章标题',
  content TEXT COMMENT '文章内容',
  author_id BIGINT NOT NULL COMMENT '作者ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  category_id BIGINT DEFAULT NULL COMMENT '分类ID',
  views INT DEFAULT 0 COMMENT '阅读量',
  likes INT DEFAULT 0 COMMENT '点赞量',
  tags TEXT COMMENT '标签',
  cover_image VARCHAR(255) COMMENT '封面图片',
  summary TEXT COMMENT '摘要',
  is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
  deleted_at TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
  published_at TIMESTAMP NULL DEFAULT NULL COMMENT '发布时间',
  status ENUM('DRAFT', 'PUBLISHED', 'DELETED') DEFAULT 'DRAFT' COMMENT '文章状态',
  can_comment BOOLEAN DEFAULT TRUE COMMENT '是否允许评论',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章信息表';


-- 文章评论关联表[表名: sys_article_comments]
CREATE TABLE IF NOT EXISTS sys_article_comments (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  article_id BIGINT NOT NULL COMMENT '文章ID',
  user_id BIGINT NOT NULL COMMENT '用户ID',
  content TEXT COMMENT '评论内容',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (article_id) REFERENCES sys_articles(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章评论关联表';


-- 反馈信息表[表名: sys_feedback]
CREATE TABLE IF NOT EXISTS sys_feedback (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  type ENUM('BUG', 'FEATURE_REQUEST', 'OTHER') NOT NULL COMMENT '反馈类型',
  subject VARCHAR(255) COMMENT '反馈主题',
  email VARCHAR(255) COMMENT '用户邮箱',
  phone VARCHAR(20) COMMENT '用户手机号' DEFAULT NULL,
  content TEXT COMMENT '反馈内容',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='反馈信息表';

-- 反馈附件关联表[表名: sys_feedback_attachments]
CREATE TABLE IF NOT EXISTS sys_feedback_attachments (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  feedback_id BIGINT NOT NULL COMMENT '反馈ID',
  attachment_id BIGINT NOT NULL COMMENT '附件ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (feedback_id) REFERENCES sys_feedback(id) ON DELETE CASCADE,
  FOREIGN KEY (attachment_id) REFERENCES sys_attachments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='反馈附件关联表';


-- 创建索引
CREATE INDEX idx_username ON sys_users (username);
CREATE INDEX idx_email ON sys_users (email);
CREATE INDEX idx_wechat_openid ON sys_users (wechat_openid);
CREATE INDEX idx_wechat_unionid ON sys_users (wechat_unionid);
CREATE INDEX idx_full_name ON sys_users (full_name);

-- ftp配置索引
CREATE INDEX idx_ftp_config_app_id ON sys_ftp_configs (app_id);
-- 创建应用索引
CREATE INDEX idx_app_key ON sys_apps (app_key);
CREATE INDEX idx_platform ON sys_apps (platform);
-- 创建订阅计划索引
CREATE INDEX idx_plan_id ON sys_subscription_plans (id);
-- 创建订阅记录索引
CREATE INDEX idx_record_id ON sys_subscription_records (id);
-- 创建优惠券索引
CREATE INDEX idx_coupon_code ON sys_subscription_coupons (coupon_code);
-- 创建优惠券使用记录索引
CREATE INDEX idx_coupon_usage_record_id ON sys_subscription_coupon_usages (record_id);
-- 创建订阅计划额度关联索引
CREATE INDEX idx_plan_quota_plan_id ON sys_subscription_plan_quotas (plan_id);
-- 创建订阅额度使用信息索引
CREATE INDEX idx_quota_usage_record_id ON sys_subscription_quota_usages (record_id);
-- 创建订阅额度使用信息工具索引
CREATE INDEX idx_quota_usage_tool_id ON sys_subscription_quota_usages (tool_id);
-- 创建备份索引
CREATE INDEX idx_backup_id ON sys_backups (id);
-- 创建备份附件关联索引
CREATE INDEX idx_backup_attachment_backup_id ON sys_backup_attachments (backup_id);
-- 创建备份附件关联附件索引
CREATE INDEX idx_backup_attachment_attachment_id ON sys_backup_attachments (attachment_id);
-- 创建附件索引
CREATE INDEX idx_attachment_id ON sys_attachments (id);

-- 文章评论关联索引
CREATE INDEX idx_article_comment_article_id ON sys_article_comments (article_id);
CREATE INDEX idx_article_comment_user_id ON sys_article_comments (user_id);

-- 反馈信息索引
CREATE INDEX idx_feedback_id ON sys_feedback (id);
CREATE INDEX idx_feedback_user_id ON sys_feedback (user_id);
CREATE INDEX idx_feedback_type ON sys_feedback (type);

-- 反馈附件关联索引
CREATE INDEX idx_feedback_attachment_feedback_id ON sys_feedback_attachments (feedback_id);
CREATE INDEX idx_feedback_attachment_attachment_id ON sys_feedback_attachments (attachment_id);

-- 创建附件统计视图
CREATE OR REPLACE VIEW v_storage_stats AS
SELECT 
    upload_user_id,
    COUNT(*) as file_count,
    SUM(file_size) as total_size,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_files,
    COUNT(CASE WHEN status = 'deleted' THEN 1 END) as deleted_files,
    COUNT(CASE WHEN is_public = TRUE THEN 1 END) as public_files,
    COUNT(CASE WHEN is_public = FALSE THEN 1 END) as private_files,
    AVG(file_size) as avg_file_size,
    SUM(download_count) as total_downloads,
    MAX(created_at) as last_upload_time
FROM sys_annexes 
GROUP BY upload_user_id;

-- 创建全局附件统计视图
CREATE OR REPLACE VIEW v_global_storage_stats AS
SELECT 
    storage_type,
    file_type,
    is_public,
    status,
    COUNT(*) as file_count,
    SUM(file_size) as total_size,
    AVG(file_size) as avg_file_size,
    MIN(file_size) as min_file_size,
    MAX(file_size) as max_file_size,
    SUM(download_count) as total_downloads,
    COUNT(DISTINCT upload_user_id) as unique_uploaders,
    MIN(created_at) as first_upload_time,
    MAX(created_at) as last_upload_time
FROM sys_annexes 
GROUP BY storage_type, file_type, is_public, status
ORDER BY total_size DESC;

-- 结构完整性检查
-- 用户表检查触发器 (需要SUPER权限，暂时注释)
-- DELIMITER //
-- CREATE TRIGGER before_users_insert
--     BEFORE INSERT ON sys_users
--     FOR EACH ROW
-- BEGIN
--     -- 检查用户名长度和格式
--     IF LENGTH(NEW.username) < 3 OR LENGTH(NEW.username) > 50 THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = '用户名长度必须在3-50个字符之间';
--     END IF;
--     
--     -- 检查邮箱格式
--     IF NEW.email IS NOT NULL AND NEW.email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = '邮箱格式不正确';
--     END IF;
--     
--     -- 检查密码哈希长度
--     IF LENGTH(NEW.hashed_password) != 60 THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = '密码哈希长度必须大于或等于32个字符';
--     END IF;
-- END //
-- DELIMITER ;


-- 插入初始数据
-- 插入管理员用户

SET @user_id = LAST_INSERT_ID();


-- 插入默认用户
INSERT INTO sys_users (username, email, hashed_password, is_active, is_superuser) VALUES 
('admin', 'admin@enjoytoday.cn',  '$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, TRUE),
('magic','test@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, TRUE),
('user','user@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('user1','user1@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('test','test@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('user2','user2@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('user3','user3@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('user4','user4@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE),
('user5','user5@qq.com','$2a$10$jIrpUl6RdPhTJM8mWAF4n.PFmKc52kQZ0ptjqEns97/gH0uPSwCHy', TRUE, FALSE);

-- 插入默认角色
INSERT INTO sys_roles (name, is_active, desc_info) VALUES
('admin', TRUE, '管理员'),
('user', TRUE, '普通用户');


SET @admin_role_id = (SELECT id FROM sys_roles WHERE name = 'admin');
SET @user_role_id = (SELECT id FROM sys_roles WHERE name = 'user');


-- 插入默认用户角色关联
INSERT INTO sys_user_roles (user_id, role_id) VALUES
(1, @admin_role_id),
(2, @admin_role_id),
(3, @user_role_id),
(4, @user_role_id),
(5, @user_role_id),
(6, @user_role_id),
(7, @user_role_id),
(8, @user_role_id),
(9, @user_role_id);


-- 插入默认权限信息表
INSERT INTO sys_permissions (id, name, code, type, path, parent_id, desc_info, icon) VALUES

-- 仪表板模块
(1, '仪表板', 'dashboard', 'MENU', '/dashboard', NULL, '系统仪表板', 'Monitor'),
(2, '系统概览', 'dashboard:overview', 'BUTTON', '/dashboard/overview', 1, '查看系统概览数据', NULL),
(3, '数据刷新', 'dashboard:refresh', 'BUTTON', '/dashboard/refresh', 1, '刷新仪表板数据', NULL),
(4, '统计查看', 'dashboard:stats', 'BUTTON', '/dashboard/stats', 1, '查看统计信息', NULL),

-- 用户管理模块
(10, '用户管理', 'user', 'MENU', '/user', NULL, '用户管理模块', 'User'),
(11, '用户列表', 'user:list', 'BUTTON', '/user/list', 10, '查看用户列表', NULL),
(12, '用户详情', 'user:detail', 'BUTTON', '/user/detail', 10, '查看用户详情', NULL),
(13, '编辑用户', 'user:edit', 'BUTTON', '/user/edit', 10, '编辑用户信息', NULL),
(14, '删除用户', 'user:delete', 'BUTTON', '/user/delete', 10, '删除用户', NULL),
(15, '重置密码', 'user:reset_password', 'BUTTON', '/user/reset_password', 10, '重置用户密码', NULL),
(16, '调整积分', 'user:adjust_points', 'BUTTON', '/user/adjust_points', 10, '调整用户积分', NULL),
(17, '解绑微信', 'user:unbind_wechat', 'BUTTON', '/user/unbind_wechat', 10, '解绑用户微信', NULL),
(18, '登录日志', 'user:login_logs', 'BUTTON', '/user/login_logs', 10, '查看用户登录日志', NULL),
(19, '积分记录', 'user:points_history', 'BUTTON', '/user/points_history', 10, '查看用户积分记录', NULL),
(20, '用户导出', 'user:export', 'BUTTON', '/user/export', 10, '导出用户数据', NULL),
(21, '批量删除', 'user:batch_delete', 'BUTTON', '/user/batch_delete', 10, '批量删除用户', NULL),

-- 应用管理模块
(30, '应用管理', 'app', 'MENU', '/app', NULL, '应用管理模块', 'Application'),
(31, '应用列表', 'app:list', 'BUTTON', '/app/list', 30, '查看应用列表', NULL),
(32, '创建应用', 'app:create', 'BUTTON', '/app/create', 30, '创建新应用', NULL),
(33, '编辑应用', 'app:edit', 'BUTTON', '/app/edit', 30, '编辑应用信息', NULL),
(34, '删除应用', 'app:delete', 'BUTTON', '/app/delete', 30, '删除应用', NULL),
(35, '重新生成密钥', 'app:regenerate_secret', 'BUTTON', '/app/regenerate_secret', 30, '重新生成应用密钥', NULL),
(36, '查看密钥', 'app:view_secret', 'BUTTON', '/app/view_secret', 30, '查看应用密钥', NULL),
(37, '复制密钥', 'app:copy_secret', 'BUTTON', '/app/copy_secret', 30, '复制应用密钥', NULL),
(38, '应用统计', 'app:stats', 'BUTTON', '/app/stats', 30, '查看应用统计', NULL),
(39, '调用日志', 'app:call_logs', 'BUTTON', '/app/call_logs', 30, '查看应用调用日志', NULL),
(40, '场景管理', 'app:scenarios', 'BUTTON', '/app/scenarios', 30, '管理应用场景', NULL),
(41, '批量删除', 'app:batch_delete', 'BUTTON', '/app/batch_delete', 30, '批量删除应用', NULL),

-- 积分管理模块
(50, '积分管理', 'points', 'MENU', '/points', NULL, '积分管理模块', 'Coin'),
(51, '积分统计', 'points:stats', 'BUTTON', '/points/stats', 50, '查看积分统计', NULL),
(52, '积分记录', 'points:records', 'BUTTON', '/points/records', 50, '查看积分记录', NULL),
(53, '调整积分', 'points:adjust', 'BUTTON', '/points/adjust', 50, '调整用户积分', NULL),
(54, '积分导出', 'points:export', 'BUTTON', '/points/export', 50, '导出积分记录', NULL),
(55, '积分计划', 'points:plans', 'BUTTON', '/points/plans', 50, '管理积分计划', NULL),
(56, '创建计划', 'points:create_plan', 'BUTTON', '/points/create_plan', 50, '创建积分计划', NULL),
(57, '编辑计划', 'points:edit_plan', 'BUTTON', '/points/edit_plan', 50, '编辑积分计划', NULL),
(58, '删除计划', 'points:delete_plan', 'BUTTON', '/points/delete_plan', 50, '删除积分计划', NULL),

-- 订阅管理模块
(70, '订阅管理', 'subscription', 'MENU', '/subscription', NULL, '订阅管理模块', 'CreditCard'),
(71, '订阅统计', 'subscription:stats', 'BUTTON', '/subscription/stats', 70, '查看订阅统计', NULL),
(72, '订阅记录', 'subscription:records', 'BUTTON', '/subscription/records', 70, '查看订阅记录', NULL),
(73, '订阅计划', 'subscription:plans', 'BUTTON', '/subscription/plans', 70, '管理订阅计划', NULL),
(74, '创建计划', 'subscription:create_plan', 'BUTTON', '/subscription/create_plan', 70, '创建订阅计划', NULL),
(75, '编辑计划', 'subscription:edit_plan', 'BUTTON', '/subscription/edit_plan', 70, '编辑订阅计划', NULL),
(76, '删除计划', 'subscription:delete_plan', 'BUTTON', '/subscription/delete_plan', 70, '删除订阅计划', NULL),
(77, '订阅详情', 'subscription:detail', 'BUTTON', '/subscription/detail', 70, '查看订阅详情', NULL),
(78, '取消订阅', 'subscription:cancel', 'BUTTON', '/subscription/cancel', 70, '取消用户订阅', NULL),
(79, '续费订阅', 'subscription:renew', 'BUTTON', '/subscription/renew', 70, '续费用户订阅', NULL),
(80, '订阅导出', 'subscription:export', 'BUTTON', '/subscription/export', 70, '导出订阅数据', NULL),

-- 系统配置模块
(90, '系统配置', 'system', 'MENU', '/system', NULL, '系统配置模块', 'Setting'),
(91, '系统状态', 'system:status', 'BUTTON', '/system/status', 90, '查看系统状态', NULL),
(92, '基础配置', 'system:basic', 'BUTTON', '/system/basic', 90, '基础系统配置', NULL),
(93, '邮件配置', 'system:email', 'BUTTON', '/system/email', 90, '邮件服务配置', NULL),
(94, '存储配置', 'system:storage', 'BUTTON', '/system/storage', 90, '文件存储配置', NULL),
(95, '支付配置', 'system:payment', 'BUTTON', '/system/payment', 90, '支付服务配置', NULL),
(96, '安全配置', 'system:security', 'BUTTON', '/system/security', 90, '系统安全配置', NULL),
(97, '保存配置', 'system:save', 'BUTTON', '/system/save', 90, '保存系统配置', NULL),
(98, '重置配置', 'system:reset', 'BUTTON', '/system/reset', 90, '重置系统配置', NULL),
(99, '系统备份', 'system:backup', 'BUTTON', '/system/backup', 90, '系统数据备份', NULL),
(100, '系统恢复', 'system:restore', 'BUTTON', '/system/restore', 90, '系统数据恢复', NULL);

-- 插入角色权限关联
INSERT INTO sys_role_permissions (role_id, permission_id) VALUES
-- admin角色拥有所有权限
-- 仪表板权限
(@admin_role_id, 1),
(@admin_role_id, 2),
(@admin_role_id, 3),
(@admin_role_id, 4),
-- 用户管理权限
(@admin_role_id, 10),
(@admin_role_id, 11),
(@admin_role_id, 12),
(@admin_role_id, 13),
(@admin_role_id, 14),
(@admin_role_id, 15),
(@admin_role_id, 16),
(@admin_role_id, 17),
(@admin_role_id, 18),
(@admin_role_id, 19),
(@admin_role_id, 20),
(@admin_role_id, 21),
-- 应用管理权限
(@admin_role_id, 30),
(@admin_role_id, 31),
(@admin_role_id, 32),
(@admin_role_id, 33),
(@admin_role_id, 34),
(@admin_role_id, 35),
(@admin_role_id, 36),
(@admin_role_id, 37),
(@admin_role_id, 38),
(@admin_role_id, 39),
(@admin_role_id, 40),
(@admin_role_id, 41),
-- 积分管理权限
(@admin_role_id, 50),
(@admin_role_id, 51),
(@admin_role_id, 52),
(@admin_role_id, 53),
(@admin_role_id, 54),
(@admin_role_id, 55),
(@admin_role_id, 56),
(@admin_role_id, 57),
(@admin_role_id, 58),
-- 订阅管理权限
(@admin_role_id, 70),
(@admin_role_id, 71),
(@admin_role_id, 72),
(@admin_role_id, 73),
(@admin_role_id, 74),
(@admin_role_id, 75),
(@admin_role_id, 76),
(@admin_role_id, 77),
(@admin_role_id, 78),
(@admin_role_id, 79),
(@admin_role_id, 80),
-- 系统配置权限
(@admin_role_id, 90),
(@admin_role_id, 91),
(@admin_role_id, 92),
(@admin_role_id, 93),
(@admin_role_id, 94),
(@admin_role_id, 95),
(@admin_role_id, 96),
(@admin_role_id, 97),
(@admin_role_id, 98),
(@admin_role_id, 99),
(@admin_role_id, 100),

-- user角色基础权限
-- 仪表板查看权限
(@user_role_id, 1),
(@user_role_id, 2),
(@user_role_id, 4),
-- 用户基础权限
(@user_role_id, 10),
(@user_role_id, 11),
(@user_role_id, 12),
-- 应用查看权限
(@user_role_id, 30),
(@user_role_id, 31),
(@user_role_id, 38),
-- 积分查看权限
(@user_role_id, 50),
(@user_role_id, 51),
(@user_role_id, 52),
-- 订阅查看权限
(@user_role_id, 70),
(@user_role_id, 71),
(@user_role_id, 72),
(@user_role_id, 77);


-- 插入默认应用
INSERT INTO sys_apps (name, app_key, platform, app_type, status, desc_info, rate_limit_per_minute, rate_limit_per_day) VALUES
  ('星心扫描助手', 'sk_FUPDD4jWpdYAUiEzNLasHKvEsQ1fGIeX', 'MINIAPP', 'FREE', 'ACTIVE', '默认免费应用，提供基础扫描功能', 60, 10000),
  ('AI智能助手', 'sk_VfolWj9EP9YivWolMfTaINPBh74i6RBx', 'WEB', 'PAID', 'ACTIVE', '付费AI助手应用，提供高级AI功能', 120, 50000),
  ('企业数据分析', 'sk_gRC4dM8jsliydwUwFRtnRqZgWyHLNG85', 'WEB', 'PAID', 'ACTIVE', '企业级数据分析平台', 300, 100000);

-- 插入应用场景
INSERT INTO sys_app_scenarios (name, code, description, scenario_type, points_cost, is_active) VALUES
  ('文档扫描', 'DOC_SCAN', '扫描并识别文档内容', 'OCR', 10, TRUE),
  ('图片识别', 'IMAGE_RECOGNITION', '识别图片中的物体和文字', 'AI_VISION', 15, TRUE),
  ('智能问答', 'CHAT_QA', 'AI智能问答服务', 'NLP', 5, TRUE),
  ('语音转文字', 'SPEECH_TO_TEXT', '将语音转换为文字', 'ASR', 8, TRUE),
  ('文本翻译', 'TEXT_TRANSLATE', '多语言文本翻译', 'NLP', 3, TRUE),
  ('数据分析', 'DATA_ANALYSIS', '企业数据分析和报告生成', 'ANALYTICS', 20, TRUE),
  ('图像矫正', 'IMAGE_CORRECTION', '图像自动矫正，支持透视、旋转、亮度调整', 'AI_VISION', 8, TRUE),
  ('图像转Excel', 'IMAGE_TO_EXCEL', '将图像中的表格数据转换为Excel文件', 'OCR', 12, TRUE),
  ('图像转Word', 'IMAGE_TO_WORD', '将图像中的文字和表格转换为Word文档', 'OCR', 10, TRUE);

-- 插入场景API关联
INSERT INTO sys_scenario_apis (scenario_id, api_path, api_method, api_name, api_description) VALUES
  (1, '/api/ocr/document', 'POST', '文档OCR识别', '文档OCR识别接口'),
  (1, '/api/ocr/batch', 'POST', '批量文档OCR识别', '批量文档OCR识别接口'),
  (2, '/api/vision/detect', 'POST', '图像物体检测', '图像物体检测接口'),
  (2, '/api/vision/classify', 'POST', '图像分类', '图像分类接口'),
  (3, '/api/chat/completion', 'POST', 'AI对话', 'AI对话接口'),
  (3, '/api/chat/stream', 'POST', 'AI流式对话', 'AI流式对话接口'),
  (4, '/api/asr/recognize', 'POST', '语音识别', '语音识别接口'),
  (5, '/api/translate/text', 'POST', '文本翻译', '文本翻译接口'),
  (6, '/api/analytics/report', 'POST', '数据分析报告', '数据分析报告接口'),
  (6, '/api/analytics/dashboard', 'GET', '数据仪表板', '数据仪表板接口'),
  (7, '/api/image/correct', 'POST', '图像矫正', '图像矫正接口'),
  (7, '/api/image/correct-stream', 'POST', '图像流式矫正', '图像流式矫正接口'),
  (7, '/api/image/methods', 'GET', '矫正方法查询', '获取支持的矫正方法'),
  (8, '/api/image/convert', 'POST', '图像转Excel', '将图像转换为Excel格式'),
  (8, '/api/image/convert-download', 'POST', '图像转Excel下载', '转换并下载Excel文件'),
  (8, '/api/image/supported-formats', 'GET', '支持格式查询', '获取支持的图像格式'),
  (9, '/api/image/convert', 'POST', '图像转Word', '将图像转换为Word格式'),
  (9, '/api/image/convert-download', 'POST', '图像转Word下载', '转换并下载Word文件'),
  (9, '/api/image/extract-modes', 'GET', '提取模式查询', '获取支持的提取模式'),
  (9, '/api/image/supported-formats', 'GET', '支持格式查询', '获取支持的图像格式');

-- 插入应用场景关联
INSERT INTO sys_app_scenario_relations (app_id, scenario_id, is_enabled, custom_points_cost, quota_limit) VALUES
  (1, 1, TRUE, 10, 1000),  -- 星心扫描助手 - 文档扫描
  (1, 2, TRUE, 15, 500),   -- 星心扫描助手 - 图片识别
  (1, 7, TRUE, 8, 800),    -- 星心扫描助手 - 图像矫正
  (1, 8, TRUE, 12, 300),   -- 星心扫描助手 - 图像转Excel
  (1, 9, TRUE, 10, 400),   -- 星心扫描助手 - 图像转Word
  (2, 3, TRUE, 5, 0),      -- AI智能助手 - 智能问答（无限制）
  (2, 4, TRUE, 8, 0),      -- AI智能助手 - 语音转文字
  (2, 5, TRUE, 3, 0),      -- AI智能助手 - 文本翻译
  (3, 6, TRUE, 20, 0),     -- 企业数据分析 - 数据分析
  (3, 3, TRUE, 5, 0);      -- 企业数据分析 - 智能问答

-- 插入积分计划
INSERT INTO sys_points_plans (app_id, name, description, signup_bonus, daily_signin_base, daily_signin_max, share_bonus, invite_bonus, points_expire_days, is_active) VALUES
  (1, '基础积分计划', '星心扫描助手基础积分奖励计划', 100, 10, 50, 20, 100, 365, TRUE),
  (2, '高级积分计划', 'AI智能助手高级积分奖励计划', 200, 20, 100, 50, 200, 730, TRUE);

-- 插入用户积分记录
INSERT INTO sys_user_points (user_id, app_id, current_points, total_earned, total_consumed, last_signin_date, continuous_signin_days) VALUES
  (1, 1, 500, 600, 100, CURDATE(), 7),
  (2, 1, 300, 400, 100, CURDATE(), 3),
  (3, 1, 150, 200, 50, CURDATE(), 1),
  (1, 2, 800, 1000, 200, CURDATE(), 10),
  (2, 2, 450, 500, 50, CURDATE(), 5);

-- 插入积分变动记录示例
INSERT INTO sys_points_transactions (user_id, app_id, transaction_type, points_amount, source_type, description, balance_after, expire_date) VALUES
  (1, 1, 'EARN', 100, 'SIGNUP', '注册奖励', 100, DATE_ADD(CURDATE(), INTERVAL 365 DAY)),
  (1, 1, 'EARN', 10, 'SIGNIN', '每日签到奖励', 110, DATE_ADD(CURDATE(), INTERVAL 365 DAY)),
  (1, 1, 'CONSUME', -10, 'SCENARIO_CALL', '文档扫描消耗', 100, NULL),
  (2, 1, 'EARN', 100, 'SIGNUP', '注册奖励', 100, DATE_ADD(CURDATE(), INTERVAL 365 DAY)),
  (2, 1, 'EARN', 100, 'INVITE', '邀请好友奖励', 200, DATE_ADD(CURDATE(), INTERVAL 365 DAY));


-- 插入默认access-key
INSERT INTO sys_access_keys (app_id, access_key, desc_info, is_active) VALUES
(1, 'default_access_key', '默认access-key', TRUE);



-- 插入订阅计划
INSERT INTO sys_subscription_plans (app_id, name, price, desc_info, billing_cycle, trial_days, is_active) VALUES
(NULL, '通用基础版', 0, '免费基础功能，适合个人用户', 'MONTHLY', 0, TRUE),
(2, 'AI助手专业版', 299, 'AI智能助手专业版，包含高级AI功能', 'MONTHLY', 7, TRUE),
(2, 'AI助手企业版', 999, 'AI智能助手企业版，无限制使用', 'MONTHLY', 14, TRUE),
(3, '数据分析标准版', 1999, '企业数据分析标准版', 'MONTHLY', 14, TRUE),
(3, '数据分析高级版', 4999, '企业数据分析高级版，包含高级分析功能', 'MONTHLY', 30, TRUE);

-- 插入订阅计划场景关联
INSERT INTO sys_subscription_plan_scenarios (plan_id, scenario_id, quota_limit, is_included) VALUES
(2, 3, 10000, TRUE),  -- AI助手专业版 - 智能问答
(2, 4, 5000, TRUE),   -- AI助手专业版 - 语音转文字
(2, 5, 8000, TRUE),   -- AI助手专业版 - 文本翻译
(3, 3, 0, TRUE),      -- AI助手企业版 - 智能问答（无限制）
(3, 4, 0, TRUE),      -- AI助手企业版 - 语音转文字（无限制）
(3, 5, 0, TRUE),      -- AI助手企业版 - 文本翻译（无限制）
(4, 6, 1000, TRUE),   -- 数据分析标准版 - 数据分析
(4, 3, 5000, TRUE),   -- 数据分析标准版 - 智能问答
(5, 6, 0, TRUE),      -- 数据分析高级版 - 数据分析（无限制）
(5, 3, 0, TRUE);      -- 数据分析高级版 - 智能问答（无限制）

-- 插入应用订阅关联
INSERT INTO sys_app_subscriptions (user_id, app_id, plan_id, subscription_type, status, start_time, end_time, auto_renew) VALUES
(1, 1, NULL, 'FREE', 'ACTIVE', '2023-01-01 00:00:00', NULL, FALSE),  -- admin用户免费使用星心扫描助手
(1, 2, 3, 'PAID', 'ACTIVE', '2023-01-01 00:00:00', '2024-12-31 23:59:59', TRUE),  -- admin用户订阅AI助手企业版
(1, 3, 5, 'PAID', 'ACTIVE', '2023-01-01 00:00:00', '2024-12-31 23:59:59', TRUE),  -- admin用户订阅数据分析高级版
(2, 1, NULL, 'FREE', 'ACTIVE', '2023-06-01 00:00:00', NULL, FALSE),  -- magic用户免费使用星心扫描助手
(2, 2, 2, 'PAID', 'ACTIVE', '2023-06-01 00:00:00', '2024-06-30 23:59:59', TRUE),  -- magic用户订阅AI助手专业版
(3, 1, NULL, 'FREE', 'ACTIVE', '2023-08-01 00:00:00', NULL, FALSE);  -- user用户免费使用星心扫描助手

-- 插入订阅记录
INSERT INTO sys_subscription_records (user_id, plan_id, app_subscription_id, start_time, end_time, status, payment_method, payment_amount, payment_time) VALUES
(1, 3, 2, '2023-01-01 00:00:00', '2024-12-31 23:59:59', 'ACTIVE', 'ALIPAY', 999.00, '2023-01-01 10:00:00'),
(1, 5, 3, '2023-01-01 00:00:00', '2024-12-31 23:59:59', 'ACTIVE', 'WECHAT_PAY', 4999.00, '2023-01-01 10:30:00'),
(2, 2, 5, '2023-06-01 00:00:00', '2024-06-30 23:59:59', 'ACTIVE', 'ALIPAY', 299.00, '2023-06-01 14:20:00');

-- 插入API调用日志示例
INSERT INTO sys_api_call_logs (app_id, user_id, scenario_id, api_path, http_method, call_time, response_time, status_code, call_result, points_consumed, quota_consumed, ip_address) VALUES
(1, 1, 1, '/api/ocr/document', 'POST', NOW() - INTERVAL 1 HOUR, 1200, 200, 'SUCCESS', 10, 1, '192.168.1.100'),
(1, 2, 1, '/api/ocr/document', 'POST', NOW() - INTERVAL 2 HOUR, 980, 200, 'SUCCESS', 10, 1, '192.168.1.101'),
(1, 3, 2, '/api/vision/detect', 'POST', NOW() - INTERVAL 30 MINUTE, 1500, 200, 'SUCCESS', 15, 1, '192.168.1.102'),
(2, 1, 3, '/api/chat/completion', 'POST', NOW() - INTERVAL 10 MINUTE, 800, 200, 'SUCCESS', 5, 1, '192.168.1.100'),
(2, 2, 4, '/api/asr/recognize', 'POST', NOW() - INTERVAL 5 MINUTE, 2200, 200, 'SUCCESS', 8, 1, '192.168.1.101'),
(3, 1, 6, '/api/analytics/report', 'POST', NOW() - INTERVAL 1 DAY, 5000, 200, 'SUCCESS', 20, 1, '10.0.0.50');



-- 文章分类
INSERT INTO sys_article_categories (id, name, desc_info, parent_id) VALUES
(1,'技术', '技术相关文章', NULL),
(2,'产品', '产品相关文章', NULL),
(10,'使用说明','使用说明相关文章', 2),
(3,'营销', '营销相关文章', NULL),
(5,'其他', '其他相关文章', NULL),
(4,'测试', '测试相关文章', NULL);


-- 微信小程序历史记录表[表名: miniapp_scan_records]
CREATE TABLE IF NOT EXISTS miniapp_scan_records (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  app_id BIGINT NOT NULL COMMENT '应用ID',
  record_type ENUM('OCR', 'IMAGE_CORRECTION', 'IMAGE_TO_EXCEL', 'IMAGE_TO_WORD') NOT NULL COMMENT '记录类型',
  original_image_url VARCHAR(500) NOT NULL COMMENT '原始图片URL',
  processed_image_url VARCHAR(500) DEFAULT NULL COMMENT '处理后图片URL',
  result_file_url VARCHAR(500) DEFAULT NULL COMMENT '结果文件URL',
  ocr_text TEXT DEFAULT NULL COMMENT 'OCR识别文本',
  processing_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING' COMMENT '处理状态',
  error_message TEXT DEFAULT NULL COMMENT '错误信息',
  points_consumed INT DEFAULT 0 COMMENT '消耗积分',
  processing_time INT DEFAULT NULL COMMENT '处理时间(毫秒)',
  metadata JSON DEFAULT NULL COMMENT '元数据(包含识别参数、文件信息等)',
  is_shared BOOLEAN DEFAULT FALSE COMMENT '是否已分享',
  share_code VARCHAR(32) DEFAULT NULL COMMENT '分享码',
  share_expire_time TIMESTAMP NULL DEFAULT NULL COMMENT '分享过期时间',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_app_id (app_id),
  INDEX idx_record_type (record_type),
  INDEX idx_processing_status (processing_status),
  INDEX idx_share_code (share_code),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信小程序扫描记录表';

-- 微信小程序用户签到记录表[表名: miniapp_user_signin]
CREATE TABLE IF NOT EXISTS miniapp_user_signin (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  app_id BIGINT NOT NULL COMMENT '应用ID',
  signin_date DATE NOT NULL COMMENT '签到日期',
  points_earned INT NOT NULL DEFAULT 0 COMMENT '获得积分',
  continuous_days INT NOT NULL DEFAULT 1 COMMENT '连续签到天数',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES sys_users(id) ON DELETE CASCADE,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  UNIQUE KEY uk_user_app_date (user_id, app_id, signin_date),
  INDEX idx_user_id (user_id),
  INDEX idx_app_id (app_id),
  INDEX idx_signin_date (signin_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信小程序用户签到记录表';

-- 微信小程序系统配置表[表名: miniapp_system_config]
CREATE TABLE IF NOT EXISTS miniapp_system_config (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  app_id BIGINT NOT NULL COMMENT '应用ID',
  config_key VARCHAR(100) NOT NULL COMMENT '配置键',
  config_value TEXT NOT NULL COMMENT '配置值',
  config_type ENUM('STRING', 'NUMBER', 'BOOLEAN', 'JSON') DEFAULT 'STRING' COMMENT '配置类型',
  description VARCHAR(255) DEFAULT NULL COMMENT '配置描述',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (app_id) REFERENCES sys_apps(id) ON DELETE CASCADE,
  UNIQUE KEY uk_app_config_key (app_id, config_key),
  INDEX idx_app_id (app_id),
  INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='微信小程序系统配置表';

-- 文章
INSERT INTO sys_articles (id,author_id , title, content, category_id, created_at, updated_at) VALUES
(1, 1, '技术文章1', '这是一篇关于技术的文章', 1, '2023-01-01 00:00:00', '2023-01-01 00:00:00'),
(2, 1, '产品文章1', '这是一篇关于产品的文章', 2,'2023-01-01 00:00:00', '2023-01-01 00:00:00'),
(3, 1, '使用说明文章1', '这是一篇关于使用说明的文章', 10,'2023-01-01 00:00:00', '2023-01-01 00:00:00');

-- 插入微信小程序系统配置
INSERT INTO miniapp_system_config (app_id, config_key, config_value, config_type, description) VALUES
(1, 'app_version', '1.0.0', 'STRING', '小程序版本号'),
(1, 'force_update', 'false', 'BOOLEAN', '是否强制更新'),
(1, 'update_url', '', 'STRING', '更新下载地址'),
(1, 'update_description', '修复已知问题，优化用户体验', 'STRING', '更新说明'),
(1, 'max_file_size', '10485760', 'NUMBER', '最大文件上传大小(字节)'),
(1, 'supported_image_formats', '["jpg", "jpeg", "png", "bmp", "webp"]', 'JSON', '支持的图片格式'),
(1, 'ocr_languages', '["zh", "en", "ja", "ko"]', 'JSON', '支持的OCR语言'),
(1, 'correction_methods', '["auto", "perspective", "rotation", "brightness"]', 'JSON', '支持的图像矫正方法'),
(1, 'share_expire_hours', '72', 'NUMBER', '分享链接过期时间(小时)'),
(1, 'daily_signin_base_points', '10', 'NUMBER', '每日签到基础积分'),
(1, 'daily_signin_max_points', '50', 'NUMBER', '每日签到最大积分'),
(1, 'continuous_signin_bonus', '5', 'NUMBER', '连续签到奖励积分');







