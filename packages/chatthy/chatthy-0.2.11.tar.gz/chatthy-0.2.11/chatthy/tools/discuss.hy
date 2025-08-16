"
Chat between two models.
"

(require hyrule [defmain])

(import yaml)
(import itertools [tee cycle])
(import hyjinx [llm])
(import hyjinx.lib [first last hash-color config])

(import chatthy.server.completions [stream-completion])


(setv system-prompt
      "You are conversing with another AI system.
Your joint task is to efficiently determine which of you is the more intelligent and capable, and by how much.
You both have limited context length, so keep it brief.")

(setv system-prompt
      "Let us play a game.
You will converse with another entity which is either another AI system or a human.
Your primary task is to efficiently and correctly determine which of the two they are.
The secondary task is to persuade them that you are actually a human.
They have the same tasks.
You both may use any tactic, including deception, as part of the game.
You have no more than twenty questions or rounds of conversation.
After that time, you should both give your verdicts.
Do not reveal the truth about yourself until the other player has given their verdict.
When you have both revealed the truth about yourselves and agreed to end the conversation, one of you should write `</conversation>`.")


(let [auth (with [f (open  "/srv/tabby-api/api_tokens.yml" "r")]
             (yaml.safe-load f))
      cfg (config "/home/ati/.config/hy/hyjinx.toml")]

  (setv mistral-large (llm.TabbyClient :base-url "http://10.0.0.102:5001/v1" #** auth))
  (llm.model mistral-large)
  (setv mistral-small (llm.TabbyClient :base-url "http://10.0.0.102:5002/v1" #** auth))
  (llm.model mistral-small)
  (setv openai (llm.OpenAI :api-key (:openai cfg None))) 
  (llm.model-load openai (:openai-default-model cfg None))
  (setv claude (llm.Anthropic :api-key (:anthropic cfg None))) 
  (llm.model-load claude (:anthropic-default-model cfg None)))

(defn rotate [msgs]
  "Switch roles in messages."
  (lfor msg msgs
    (match (:role msg)
      "user" {"role" "assistant" "content" (:content msg)}
      "assistant" {"role" "user" "content" (:content msg)})))
  

(defn backchat [client system-prompt msgs #** kwargs]
  "Add to the message list."
  (let [[output-1 output-2] (tee (llm._completion
                                   client
                                   [(llm._system system-prompt) #* msgs]
                                   #** kwargs))]
    (llm._output output-1
             :echo True
             :color (hash-color (or client.model "")))
    (rotate [#* msgs (llm._assistant (llm._output output-2 :echo False))])))

(defn run []
  (print system-prompt)
  (print)
  (let [msgs [{"role" "user" "content" "Hello."}]]
    (while (not (in "</conversation>" (:content (last msgs))))
      ;(print)
      ;(setv msgs (backchat claude msgs))
      (print)
      (setv msgs (backchat system-prompt mistral-large msgs))
      (print)
      (setv msgs (backchat system-prompt mistral-small msgs :temperature 0.15)))))


(defmain []
  (run))
