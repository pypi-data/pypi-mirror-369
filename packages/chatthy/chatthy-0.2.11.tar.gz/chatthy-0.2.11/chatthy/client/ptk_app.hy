"
Prompt-toolkit application for simple chat REPL.
"

(import hy [mangle])
(require hyrule [defmain])

(import hyrule [assoc inc dec])
(import hyjinx.lib [first rest slurp sync-await])
(import itertools [batched])

(import asyncio)
(import clipman)
(import flatlatex)
(import re)
(import os)
(import colorist [Color Effect])
(import pathlib [Path])
(import shutil [get-terminal-size])
(import shlex)

(import prompt-toolkit [ANSI])
(import prompt-toolkit.application [Application get-app-or-none])
(import prompt_toolkit.layout [WindowAlign])
(import prompt_toolkit.layout.dimension [Dimension])
(import prompt-toolkit.document [Document])
(import prompt-toolkit.filters [Condition to-filter is-multiline has-focus])
(import prompt-toolkit.filters [Condition to-filter is-multiline has-focus])
(import prompt-toolkit.formatted-text [to-plain-text])
(import prompt-toolkit.key-binding [KeyBindings])
(import prompt_toolkit.key_binding.bindings.page_navigation [scroll_page_up scroll_page_down])
(import prompt-toolkit.layout.containers [HSplit VSplit Window])
(import prompt-toolkit.layout.layout [Layout])
(import prompt-toolkit.patch-stdout [patch-stdout])
;(import prompt-toolkit.styles [Style])
(import prompt-toolkit.widgets [Label HorizontalLine SearchToolbar TextArea Frame])
(import prompt-toolkit.shortcuts [input-dialog])

(import prompt-toolkit.styles.pygments [style-from-pygments-cls])
(import prompt-toolkit.lexers [PygmentsLexer])
(import pygments.lexers [MarkdownLexer])
(import pygments.styles [get-style-by-name])

(import chatthy.client [state])
(import chatthy.client.client [server-rpc])


;; TODO Ctrl-C cancel generation -- send a message, set a flag, check for each chunk.
;; TODO allow click to focus

;; * handlers, general functions
;; ----------------------------------------------------------------------------

(defn quit []
  "Gracefully quit - cancel all tasks."
  (for [t (asyncio.all-tasks)]
    :if (not (is t (asyncio.current-task)))
    (t.cancel)))
  

;; * handlers
;; ----------------------------------------------------------------------------

(defn accept-handler [buffer]
  "Dispatch to handler based on mode."
  (cond
    input-field.command (command-input-handler buffer)
    input-field.edit (edit-input-handler buffer)
    :else (queue-input-handler buffer)))

(defn queue-input-handler [buffer]
  "Put the input in the queue."
  ;; the put is async, but called from sync function
  (when buffer.text
    (sync-await (.put state.input-queue
                      {"method" (if input-field.vdb
                                  "vdb"
                                  "chat")
                       "line" buffer.text}))
    ;; Explicitly require Ctrl-v to use RAG every time
    (setv input-field.vdb False))
  (mode-text)
  ;; TODO when image teed up, put the image-message in appropriately
  None)
  
(defn command-input-handler [buffer]
  "Send client command, or server RPC, from the input buffer."
  (setv input-field.command False)
  (when buffer.text
    (let [arglist (shlex.split buffer.text)
          method (first arglist)
          ;; strip leading : from kws, so :key -> "key"
          ;; and mangle kw, so "-" -> "_"
          kwargs (dfor [k v] (batched (rest arglist) 2)
                   (mangle (re.sub "^:" "" k)) v)]
      (assoc kwargs "chat" (:chat kwargs state.chat)) ; default to current chat
      (client-command method #** kwargs)))
  (mode-text)
  None)

(defn client-command [method #** kwargs]
  "Client commands are parsed here.
  Commands that don't match to client commands are conveyed as server RPCs."
  (match [method (first kwargs)]
    ;; TODO  image queueing up here
    ;;       format and send to input queue
    ["load" "chat"]
    (set-chat :chat (:chat kwargs))

    ["load" "image"]
    (raise NotImplementedError)

    ["load" "input"]
    (input-text (slurp (:input kwargs)) :multiline True)

    ["load" "ws"] 
    (let [fname (. (Path (:ws kwargs)) name)
          text (.strip (slurp (:ws kwargs)))]
      (output-text f"{fname}\n\n")
      (output-text f"{text}\n\n")
      (sync-await (server-rpc "ws"
                    :provider state.provider
                    :fname fname
                    :text text
                    #** kwargs)))

    ["load" "profile"] (setv state.profile (:profile kwargs))

    ["load" "provider"] (setv state.provider (:provider kwargs))

    ["load" "prompt"] (setv state.prompt-name (:prompt kwargs))

    _ (sync-await (server-rpc method :provider state.provider :prompt-name state.prompt-name #** kwargs)))

  (title-text))

(defn edit-input-handler [buffer]
  "Replace a specific message with the buffer text."
  ;; the put is async, but called from sync function
  (setv input-field.edit False)
  (when buffer.text
    (sync-await
      (server-rpc "replace"
        :chat state.chat
        :content buffer.text
        :index input-field.edit-index)))
  (mode-text)
  None)

  
;; * setters, app state, text fields
;; ----------------------------------------------------------------------------

(defn set-input-prompt [n w]
  "Set the input field text prompt."
  (cond
    n "⋮ "
    input-field.command (ANSI f"{Color.RED}: ")
    input-field.edit (ANSI f"{Color.MAGENTA}> ")
    input-field.multiline (ANSI f"{Color.BLUE}> ")
    :else (ANSI f"{Color.GREEN}> ")))
  
(defn set-chat [* [chat None]]
  "Set the chat id."
  (when chat
    (setv state.chat chat)
    (setv input-field.text "")
    (setv output-field.text "")
    (sync-await (server-rpc "messages" :chat chat)))
  (title-text))

(try
  (clipman.init)
  (except [clipman.exceptions.UnsupportedError]))
  

(setv kb (KeyBindings))

(setv status-field (Label :text "" :align WindowAlign.RIGHT :style "class:reverse"))
(setv title-field (Label :text "" :align WindowAlign.LEFT :style "class:reverse"))
(setv mode-field (Label :text ""
                        :width (fn [] (inc (len (to-plain-text mode-field.text))))
                        :align WindowAlign.RIGHT))
                        ;;:style "class:reverse"))
(setv output-field (TextArea :text ""
                             :wrap-lines True
                             :lexer (PygmentsLexer MarkdownLexer)
                             :read-only True))
(setv input-field (TextArea :multiline False
                            :height (Dimension :min 1 :max 3)
                            :wrap-lines True
                            :get-line-prefix set-input-prompt
                            :accept-handler accept-handler))

;; initialise the input field state
(setv input-field.multiline False)
(setv input-field.command False)
(setv input-field.edit False)
(setv input-field.edit-index 0)
(setv input-field.vdb False)
  

;; * the REPL app and state-setting functions
;; ----------------------------------------------------------------------------

(defclass REPLApp [Application]

  (defn __init__ [self] 
    "Set up the full-screen application, widgets, style and layout."

    (let [ptk-style (style-from-pygments-cls (get-style-by-name (:style state.cfg "friendly_grayscale")))
          padding (Window :width 2)]
      (setv container (HSplit [(VSplit [title-field status-field])
                               (VSplit [padding output-field padding]) 
                               ;(HorizontalLine) 
                               (VSplit [input-field mode-field])]))
      (title-text)
      (output-help)
      (.__init__ (super) :layout (Layout container :focused-element input-field)
                         :key-bindings kb
                         :style ptk-style
                         :mouse-support True
                         :full-screen True))))

(defn invalidate []
  "Redraw the app."
  (let [app (get-app-or-none)]
    (when app
      (.invalidate app))))
  

;; * printing functions
;; ----------------------------------------------------------------------------

(defn title-text []
  "Show the title."
  (setv title-field.text f"{state.profile} - {state.chat} ({state.token-count}+{state.workspace-count}) [{state.prompt-name}@{state.provider}] ")
  (invalidate))

(defn input-text [text * [multiline False] [command False] [edit False] [index 0]]
  "Set the input field text for editing."
  (let [term (get-terminal-size)]
    (setv input-field.command command)
    (setv input-field.edit edit)
    (setv input-field.edit-index index)
    (setv input-field.multiline multiline)
    (if multiline
      (setv input-field.window.height (Dimension (// term.lines 2)))
      (setv input-field.window.height (Dimension :max 3 :min 1)))
    (setv input-field.document (Document :text (.strip text) :cursor-position 0))
    (mode-text)))

(defn render-latex [s]
  "Render latex strings using flatlatex."
  (let [conv (flatlatex.converter)
        pattern r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)"
        parts (re.split r"```.*?```" s :flags re.DOTALL)]

    (defn safe-convert [text]
      (if (.strip text)
        (try
          f"{text} CONV: {(cut (conv.convert text) 2 -2)}" ;; move to right of term
          (except [flatlatex.latexfuntypes.LatexSyntaxError]
            f"ERR: {text}"))
        text))

    (for [i (range 0 (len parts) 2)]
      (setv (get parts i)
            (re.sub pattern
                    (fn [m] (safe-convert (m.group 0)))
                    (get parts i)
                    :flags re.DOTALL)))
    (.join "" parts)))

(defn output-text [output [replace False]]
  "Append (replace) output to output buffer text.
  Replaces text of output buffer.
  Moves cursor to the end."
  (let [new-text (if replace
                   output
                   (+ output-field.text output))
        tabbed-text (.replace new-text "\t" "    ")
        latex-rendered-text tabbed-text]
        ;; FIXME
        ;latex-rendered-text (render-latex tabbed-text)]
    (setv output-field.document (Document :text latex-rendered-text :cursor-position (len latex-rendered-text))))
  (invalidate))

(defn output-help []
  "Show the help text."
  (output-text (slurp (+ (os.path.dirname __file__) "/client-help.md"))))

(defn output-clear []
  "Nuke the output window."
  (setv output-field.text ""))

(defn status-text [text]
  "Set the status field text. Parses ANSI codes."
  (setv status-field.text (ANSI text))
  (invalidate))

(defn mode-text []
  "Set the mode field text. Parses ANSI codes."
  (let [modeline ""]
    (when input-field.command
      (setv modeline (.join " " [modeline f"{Color.RED}{Effect.REVERSE}command{Effect.REVERSE-OFF}{Color.OFF}"])))
    (when input-field.edit
      (setv modeline (.join " " [modeline f"{Color.MAGENTA}{Effect.REVERSE}edit {input-field.edit-index}{Effect.REVERSE-OFF}{Color.OFF}"])))
    (when input-field.multiline
      (setv modeline (.join " " [modeline f"{Color.BLUE}{Effect.REVERSE}multiline{Effect.REVERSE-OFF}{Color.OFF}"])))
    (when input-field.vdb
      (setv modeline (.join " " [modeline f"{Color.CYAN}{Effect.REVERSE}vdb:{state.rag-provider}{Effect.REVERSE-OFF}{Color.OFF}"])))
    (setv mode-field.text (ANSI modeline))
    (invalidate)))


;; * global key bindings
;;
;;   Take care: many common things like ctrl-m (return) or ctrl-h (backspace)
;;   interfere with normal operation.
;; ----------------------------------------------------------------------------

(defn [(kb.add "f1")] _ [event]
  "Pressing F1 will display some help text."
  (output-help))

(defn [(kb.add "c-q")] _ [event]
  "Pressing Ctrl-q  will cancel all tasks,
  including the REPLApp instance, and so
  exit the user interface."
  (event.app.exit)
  (quit))

;; TODO
(defn [(kb.add "c-c")] _ [event]
  "Abandon the current generation.")

#_(defn [(kb.add "c-p")] _ [event]
    "Set the active prompt"
    (with [(patch-stdout)] ; does it do anything?
      (setv state.prompt-name
            (sync-await
              (.run-async
                (input-dialog :title "Set prompt name" :text "Please type the name of your prompt"))))))

(defn :async [(kb.add "c-l")] _ [event]
  "Request list of messages.
  On receipt, replace the output with it."
  (await (server-rpc "messages" :chat state.chat)))
  ;(invalidate))

(defn [(kb.add "home")] _ [event]
  "Pressing HOME will scroll the output to the start."
  (event.app.layout.focus output-field.window)
  (setv output-field.document (Document :text output-field.text :cursor-position 0)))

(defn [(kb.add "end")] _ [event]
  "Pressing END will scroll the output to the end."
  (event.app.layout.focus output-field.window)
  (setv output-field.document (Document :text output-field.text :cursor-position (len output-field.text))))

(defn [(kb.add "pageup") (kb.add "c-b")] _ [event]
  "Pressing PGUP or Ctrl-b will scroll the output backwards."
  (event.app.layout.focus output-field.window)
  (scroll_page_up event))

(defn [(kb.add "pagedown") (kb.add "c-f")] _ [event]
  "Pressing PGDOWN or Ctrl-f will scroll the output forwards."
  (event.app.layout.focus output-field.window)
  (scroll_page_down event))
  
(defn [(kb.add "tab")] _ [event]
  "Pressing tab will toggle command mode."
  (event.app.layout.focus input-field)
  (let [term (get-terminal-size)]
    (if input-field.command
      (do ;; -> chat mode
        (setv input-field.command False)
        (mode-text))
      (do ;; -> command mode
        (setv input-field.command True)
        (setv input-field.edit False)
        (mode-text)))))


;; * input-field key bindings
;; ----------------------------------------------------------------------------

(defn [(kb.add "s-tab" :filter (has-focus input-field))] _ [event]
  "Pressing shift-tab will toggle focus between input and output."
  (event.app.layout.focus output-field))

(defn [(kb.add "c-v" :filter (has-focus input-field))] _ [event]
  "Pressing Ctrl-v will toggle vdb RAG."
  (setv input-field.vdb (not input-field.vdb))
  (mode-text))

(defn [(kb.add "escape" "m" :filter (Condition (fn [] input-field.multiline)))] _ [event]
  "Pressing Escape-m (Alt-m) will toggle multi-line input."
  ;; -> single-line
  (setv input-field.window.height (Dimension :min 1 :max 3))
  (setv input-field.multiline False)
  (mode-text))

(defn [(kb.add "escape" "m" :filter (Condition (fn [] (not input-field.multiline))))] _ [event]
  "Pressing Escape-m (Alt-m) will toggle multi-line input."
  (let [term (get-terminal-size)]
    ;; -> multi-line
    (setv input-field.window.height (Dimension (// term.lines 2)))
    (setv input-field.multiline True)
    (mode-text)))

(defn [(kb.add "escape" "e" :filter (Condition (fn [] input-field.edit)))] _ [event]
  "Pressing Escape-e (Alt-e) will toggle chat edit mode."
  (setv input-field.edit False)
  (mode-text))

(defn [(kb.add "escape" "e" :filter (Condition (fn [] (not input-field.edit))))] _ [event]
  "Pressing Escape-e (Alt-e) will toggle chat edit mode."
  (setv input-field.edit True)
  (setv input-field.command False)
  (sync-await (server-rpc "message" :index input-field.edit-index :chat state.chat))
  (mode-text))

(defn [(kb.add "c-up" :filter (Condition (fn [] input-field.edit)))] _ [event]
  "Pressing ctrl-up will select previous chat message."
  (setv input-field.edit-index (dec input-field.edit-index))
  (sync-await (server-rpc "message" :index input-field.edit-index :chat state.chat))
  (mode-text))

(defn [(kb.add "c-down" :filter (Condition (fn [] input-field.edit)))] _ [event]
  "Pressing ctrl-down will select next chat message."
  (setv input-field.edit-index (inc input-field.edit-index))
  (sync-await (server-rpc "message" :index input-field.edit-index :chat state.chat))
  (mode-text))

(defn [(kb.add "c-c" :filter (Condition (fn [] input-field.edit)))] _ [event]
  "Pressing ctrl-c will cancel the chat message edit."
  (setv input-field.edit False)
  (mode-text))



;; * output-field key bindings
;; ----------------------------------------------------------------------------

(defn [(kb.add "s-tab" :filter (has-focus output-field))] _ [event]
  "Pressing shift-tab will toggle focus between input and output."
  (event.app.layout.focus input-field))

(defn [(kb.add "y" :filter (has-focus output-field))] _ [event]
  "Pressing 'y' (yank) will send the output field selection to the clipboard."
  (when output-field.buffer.selection-state
    (try
      (clipman.copy (. (output-field.buffer.copy-selection) text))
      (except [clipman.exceptions.UnsupportedError]))))


;; * instantiate the singleton
;; ----------------------------------------------------------------------------

(setv app (REPLApp))

