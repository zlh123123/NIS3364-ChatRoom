# NIS3364-ChatRoom
NIS3364计算机网络大作业

数据库

1. **用户表 (`users`)**
   - `user_id` (主键，唯一标识用户)
   - `username` (用户名称，唯一)
   - `password` (用户密码，通常保存为哈希)
   - `profile_picture` (用户头像的URL)
   - `created_at` (用户注册时间)
2. **消息表 (`messages`)**
   - `message_id` (主键，唯一标识每条消息)
   - `sender_id` (外键，指向 `users` 表中的用户ID)
   - `receiver_id` (可以为 `NULL`，指向 `users` 表中的用户ID，用于私聊，世界频道时为 `NULL`)
   - `channel` (枚举值，标识消息类型：`world` 或 `private`)
   - `content` (消息内容，文本)
   - `file_url` (可选，指向附件的URL)
   - `created_at` (消息发送时间)
3. **频道表 (`channels`)**
   - `channel_id` (主键，唯一标识频道)
   - `channel_name` (频道名称，唯一)
   - `description` (频道描述)
   - `created_at` (频道创建时间)
4. **用户频道关系表 (`user_channels`)** (用于管理用户与频道之间的关系)
   - `user_id` (外键，指向 `users` 表中的用户ID)
   - `channel_id` (外键，指向 `channels` 表中的频道ID)
5. **文件表 (`files`)** (用于存储文件的元信息)
   - `file_id` (主键，唯一标识文件)
   - `user_id` (外键，上传文件的用户ID)
   - `file_type` (文件类型，如图片、文档、音频等)
   - `file_url` (文件存放的URL)
   - `uploaded_at` (上传时间)
