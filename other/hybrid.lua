-- Гибридный
-- Display time for all images
local json = require "json"

local IMAGE_TIME = 10

--local SWITCH_TIME = 0.4
local SWITCH_TIME = tonumber(sys.get_env "FADE_TIME" or error "INFOBEAMER_ENV_FADE_TIME unset")

local ROTATE = 0

local BLACK_SCREEN = false
local FONT = nil
local TEXT = nil

if pcall (
    function()
        FONT = resource.load_font "FreeSans.ttf"
        TEXT = resource.load_file ".ip"
        TEXT = string.gsub(TEXT, '\n', ' ')
    end
    )
then
    print "font and ip_file found"
else
    print "no font or ip_file"
end

local function draw_ip()
    if FONT and TEXT then
        FONT:write(30, 10, TEXT, 30, 1,1,1,1)
    end
end
----------------------------------------------------------

gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)

function rotate(degree)
    if degree == 0 then
        return function() end
    elseif degree == 90 then
        WIDTH, HEIGHT = HEIGHT, WIDTH
        return function()
            gl.translate(HEIGHT, 0)
            gl.rotate(90, 0, 0, 1)
        end
    elseif degree == 180 then
        return function()
            gl.translate(WIDTH, HEIGHT)
            gl.rotate(180, 0, 0, 1)
        end
    elseif degree == 270 then
        WIDTH, HEIGHT = HEIGHT, WIDTH
        return function()
            gl.translate(0, WIDTH)
            gl.rotate(-90, 0, 0, 1)
        end
    else
        error("unsupported rotation")
    end
end

function mirror(fn)
    return function()
        fn()
    end
end

local function cycled(items, offset)
    offset = offset % #items + 1
    return items[offset], offset
end

local fade_start = sys.now()
local fade_needed = true

local function image(filename)
    local img, start
    return {
        prepare = function()
            img = resource.load_image(filename)
            fade_start = sys.now()
        end;
        start = function()
            start = sys.now()
        end;
        draw = function()
            local delta = sys.now() - fade_start
            local delta2 = IMAGE_TIME - delta
            if fade_needed and delta < SWITCH_TIME then
                local progress = delta / SWITCH_TIME
                util.draw_correct(img, 0, 0, WIDTH, HEIGHT, progress)
            elseif fade_needed and delta2 < SWITCH_TIME then
                local progress = delta2 / SWITCH_TIME
                util.draw_correct(img, 0, 0, WIDTH, HEIGHT, progress)
            else
                util.draw_correct(img, 0, 0, WIDTH, HEIGHT)
            end
            if BLACK_SCREEN then
                draw_ip()
            end
            return ((sys.now() - start < IMAGE_TIME) or not fade_needed)
        end;
        dispose = function()
            img:dispose()
        end;
    }
end

local function video(filename)
    local vid, start
    return {
        prepare = function()
            print "video prepare"
            loop_needed = not fade_needed
            vid = util.videoplayer(filename, {loop=loop_needed, paused=true, audio=true})
            fade_start = sys.now()
        end;
        start = function()
            print "video start"
            vid:start()
        end;
        draw = function()
            local state, width, height = vid:state()
            util.draw_correct(vid, 0, 0, WIDTH, HEIGHT)
            return state ~= "finished" and state ~= "error"
        end;
        dispose = function()
            print "video dispose"
            vid:dispose()
        end;
    }
end

local function Runner(scheduler)
    local cur, nxt, old

    local function prepare()
        assert(not nxt)
        nxt = scheduler.get_next()
        nxt.prepare()
    end
    local function down()
        assert(not old)
        old = cur
        cur = nil
    end
    local function switch()
        assert(nxt)
        cur = nxt
        cur.start()
        nxt = nil
    end
    local function dispose()
        if old then
            old.dispose()
            old = nil
        end
    end

    local function tick()
        if not nxt then
            prepare()
        end
        dispose()
        if not cur then
            switch()
        end
        if not cur.draw() then
            down()
        end
    end

    return {
        tick = tick;
    }
end

local function Scheduler()
    local medias = {}
    local medialist = {}

    local function update_list()
        medialist = {}
        for filename, media in pairs(medias) do
            medialist[#medialist+1] = media
        end
        table.sort(medialist, function(a,b)
            return a.sort_key < b.sort_key
        end)
    end


    local config
    util.file_watch("playlist", function(content)
        config = json.decode(content)
        fade_needed = not (#config.files == 1)
        for idx = 1, #config.files do
            local filename = config.files[idx].name
            print (filename)
            local handler
            if config.files[idx].type == 'vid' then
                handler = video
            elseif config.files[idx].type == 'url' then
                handler = video
            else
                handler = image
            end
            medias[filename] = {
                handler = handler,
                filename = filename,
                sort_key = idx,
            }
            update_list()
        end
    end)

    IMAGE_TIME = config.interval

    ROTATE = config.rotate

    BLACK_SCREEN = config.blackscreen

    local media_idx = 0

    local function print_playlist()
        print "-------[ playing ]---------"
        for idx = 1, #medialist do
            print(("%5s %s"):format(idx == media_idx and "-->" or "", medialist[idx].filename))
        end
        print "---------------------------"
    end

    local function get_next()
        print_playlist()
        local media
        media, media_idx = cycled(medialist, media_idx)
        return media.handler(media.filename)
    end

    return {
        get_next = get_next;
    }
end

local scheduler = Scheduler()
local runner = Runner(scheduler)

local screen_setup = mirror(rotate(ROTATE))

assert(sys.provides "openfile", "info-beamer pi version required")


function node.render()
	screen_setup()
    runner.tick()
end
