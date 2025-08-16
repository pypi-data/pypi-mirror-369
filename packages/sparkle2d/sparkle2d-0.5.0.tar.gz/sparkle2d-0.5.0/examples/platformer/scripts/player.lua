-- Player Lua script
-- Bu script hot-reload ile çalışır

local player_id = nil
local player_speed = 100
local jump_force = 200
local gravity = -500

function start()
    print("Player script başlatıldı!")
    
    -- Player sprite oluştur
    player_id = spawn_sprite("assets/sprites/player.png", 100, 100)
    tag(player_id, "player")
    
    -- Input bağlantıları
    bind("move_left", "A,LEFT")
    bind("move_right", "D,RIGHT") 
    bind("jump", "SPACE")
    
    -- Kamera player'ı takip etsin
    camera_follow(player_id, 0.1)
    
    -- Event dinleyicisi
    on("player_jump", function()
        print("Player zıpladı!")
        sfx("jump.wav")
    end)
end

function update(dt)
    if not player_id then return end
    
    local vx = 0
    local vy = 0
    
    -- Hareket input'u
    if action_down("move_left") then
        vx = -player_speed
    elseif action_down("move_right") then
        vx = player_speed
    end
    
    -- Zıplama input'u
    if action_pressed("jump") then
        vy = jump_force
        emit("player_jump", {force = jump_force})
    end
    
    -- Yerçekimi
    vy = vy + gravity * dt
    
    -- Player pozisyonunu güncelle
    local entity = get_entity(player_id)
    if entity then
        local transform = entity:get_component("Transform")
        if transform then
            transform.x = transform.x + vx * dt
            transform.y = transform.y + vy * dt
            
            -- Yer ile çarpışma kontrolü
            if transform.y < 50 then
                transform.y = 50
            end
        end
    end
end

function on_key_press(key)
    if key == "ESCAPE" then
        print("Oyundan çıkılıyor...")
        -- Oyun çıkış eventi gönder
        emit("game_exit", {})
    end
end

print("Player script yüklendi!")
