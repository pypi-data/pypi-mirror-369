"
Chat completion and message list management functions.
"

(require hyrule [case])
(require hyjinx [defmethod])

(import re)

(import hyjinx [llm first last config hash-id coroutine])

(import chatthy.embeddings [token-count])
(import chatthy.server.state [cfg])


(defn extract-rag-output [#^ str text]
  "Use tags and regex to extract the text between `<rag:output>` and `</rag:output>`,
  that resulted from the reply of the model to the instruction from `vdb-extracts`
  or `vdb-summaries`."
  (.join "\n"
    (re.findall r"<rag:output>\s*(.*?)\s*</rag:output>" text :flags re.DOTALL)))

(defn extract-tool-output [#^ str text]
  "Use tags and regex to extract the text between `<tool:output>` and `</tool:output>`."
  (.join "\n"
    (re.findall r"<tool:output>\s*(.*?)\s*</tool:output>" text :flags re.DOTALL)))

(defn remove-think-tags [#^ str text]
  "Use tags and regex to remove text in `<think>` and `</think>` tags.
  QwQ does not always produce the opening tag."
  (re.sub r"^(.*?)\s*</think>\s*" "" 
    (re.sub r"^<think>\s*(.*?)\s*</think>\s*" "" text :flags re.DOTALL)
    :flags re.DOTALL))

(defn truncate [messages * provider [dropped []] [space (:max-tokens cfg 600)]]
  "Shorten the chat history if it gets too long, in which case
  split it and return two lists, the kept messages, and the dropped messages (in pairs).
  Use `space` to preserve space for new output or other messages that are not
  to be dropped.
  Returns `[messages, dropped]`."
  ;; TODO: test this function more thoroughly
  (let [context-length (:context-length (get cfg "providers" provider)
                                        (:context-length cfg 30000))
        ;; Any system message must be in the first position
        ;; or will be silently discarded.
        system-msg (when (and messages
                              (= (:role (first messages))
                                 "system"))
                     (:content (first messages)))
        ;; We assume alternating pairs, 
        chat-msgs (lfor m messages
                    :if (not (= (:role m) "system"))
                    m)
        ;; and need enough space to include chat msgs + system msg + new text.
        truncation-length (- context-length space)
        token-length (token-count messages)]
    (if (> token-length truncation-length)
      ;; If the total is too long, move the first two non-system messages
      ;; to the discard list and recurse.
      (let [kept (cut chat-msgs 2 None)
            new-dropped (+ dropped (cut chat-msgs 0 2))]
        (if system-msg
          (truncate (+ [system-msg] kept) :dropped new-dropped :space space :provider provider)
          (truncate kept :dropped new-dropped :space space :provider provider)))
      [messages dropped])))

(defn rotate [messages [user "user"] [assistant "assistant"]]
  "Switch user and assistant roles in messages."
  (lfor msg messages
    (case (:role msg)
      user {"role" assistant "content" (:content msg)}
      assistant {"role" user "content" (:content msg)}
      else msg)))

(defn provider [client-name]
  "Get the API client object from the config."
  (let [client None
        cfg (:providers cfg)
        provider-config (.copy (get cfg client-name)) ; so it's there next time
        context-length (.pop provider-config "context_length" None) ; can't be passed to model
        scheme (.pop provider-config "scheme" "tabby")
        api-key (.pop provider-config "api_key" None)
        model (.pop provider-config "model" None)
        ;; default generation parameters (e.g. temperature)
        ;; are set under the "params" key in provider-config
        client (match scheme
                 "anthropic" (llm.AsyncAnthropic :api-key api-key #** provider-config)
                 "openai" (llm.AsyncOpenAI :api-key api-key #** provider-config)
                 "tabby" (llm.AsyncTabbyClient :api-key api-key #** provider-config)
                 "deepinfra" (llm.AsyncOpenAI :api-key api-key #** provider-config))]
    (when model
      (llm.model-load client model))
    client))

(defmethod :async stream-completion [#^ str client-name #^ list messages #** kwargs]
  "Generate a batched streaming completion using the router API endpoint."
  (let [client (provider client-name)
        batch-size (:batch cfg 1)
        chunks []]
    (for [:async chunk (stream-completion client messages #** kwargs)]
      (if (< (len chunks) batch-size)
        (.append chunks chunk)
        (do
          (.append chunks chunk)
          (yield (.join "" chunks))
          (setv chunks []))))
    (when chunks
      (yield (.join "" chunks)))))

(defmethod :async stream-completion [#^ llm.AsyncOpenAI client #^ list messages * [stream True] [max-tokens 4000] #** kwargs]
  "Generate a streaming completion using the chat completion endpoint."
  (let [;; clean non-content fields
        ;; TODO form special image message here
        messages (lfor m messages
                       :if (in (:role m) ["user" "assistant" "system"])
                       {"role" (:role m)
                        "content" (:content m)})
        stream (await (client.chat.completions.create
                        :model (.pop kwargs "model" (getattr client "model" None))
                        :messages messages
                        :stream stream
                        :max-tokens max-tokens
                        #** client._defaults
                        #** kwargs))]
    (for [:async chunk stream :if chunk.choices]
      (let [text (. (. (first chunk.choices) delta) content)]
        (if text
          (yield text)
          (yield ""))))))

(defmethod :async stream-completion [#^ llm.AsyncAnthropic client #^ list messages * [max-tokens 4000] #** kwargs]
  "Generate a streaming completion using the messages endpoint."
  (let [system-messages (.join "\n"
                               (lfor m messages
                                     :if (= (:role m) "system")
                                     (:content m)))
        ;; clean non-content fields
        ;; TODO form special image message here
        messages (lfor m messages
                       :if (in (:role m) ["user" "assistant"])
                       {"role" (:role m)
                        "content" (:content m)})]
    (with [:async stream (client.messages.stream
                           :model (.pop kwargs "model" (getattr client "model" "claude-3-5-sonnet"))
                           :system system-messages
                           :messages messages
                           :max-tokens max-tokens
                           #** client._defaults
                           #** kwargs)]
      (for [:async text stream.text-stream :if text]
        (yield text)))))

