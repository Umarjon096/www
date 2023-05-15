-- at which intervals should the screen switch to the
-- next image?
local INTERVAL = 10

-- enough time to load next image
local SWITCH_DELAY = 1

-- transition time in seconds.
-- set it to 0 switching instantaneously
local SWITCH_TIME = 1.0

assert(SWITCH_TIME + SWITCH_DELAY < INTERVAL,
    "INTERVAL must be longer than SWITCH_DELAY + SWITCHTIME")

local json = require "json"

local config
util.file_watch("playlist", function(content)
    config = json.decode(content)
end)

INTERVAL = config.interval

pp(config.files)

local pic_count = 0
pic_count = #config.files

gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)

local pictures = util.generator(function()
    return config.files -- sort files by filename
end)

node.event("content_remove", function(filename)
    pictures:remove(filename)
end)

local current_image, fade_start

local function next_image()
    local next_image_name = pictures.next()
    print("now loading " .. next_image_name)
    last_image = current_image
    current_image = resource.load_image(next_image_name)
    fade_start = sys.now()
end

if not (pic_count == 1) then
util.set_interval(INTERVAL, next_image)
end
next_image()

function node.render()
    gl.clear(0,0,0,1)
    local delta = sys.now() - fade_start - SWITCH_DELAY
    if last_image and delta < 0 then
        util.draw_correct(last_image, 0, 0, WIDTH, HEIGHT)
    elseif last_image and delta < SWITCH_TIME then
        local progress = delta / SWITCH_TIME
        util.draw_correct(last_image, 0, 0, WIDTH, HEIGHT, 1 - progress)
        util.draw_correct(current_image, 0, 0, WIDTH, HEIGHT, progress)
    else
        if last_image then
            last_image:dispose()
            last_image = nil
        end
        util.draw_correct(current_image, 0, 0, WIDTH, HEIGHT)
    end
end
