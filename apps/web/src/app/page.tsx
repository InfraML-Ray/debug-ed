"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, ChatResponse, Curriculum, Lesson, Me } from "@/lib/api";
import { isDemo, signIn, signOut } from "@/lib/auth";

type View = "companion" | "curriculum" | "lessons";
type Turn = { role: "user" | "assistant"; text: string; sources?: string[] };
const suggestions = [
  "Draft a 40-minute lesson for my selected curriculum",
  "Suggest an activity for learners who need extra support",
  "Help me check understanding with an exit ticket",
];
const messageOf = (error: unknown) =>
  error instanceof Error ? error.message : "Something went wrong. Please try again.";

export default function Workspace() {
  const [view, setView] = useState<View>("companion");
  const [me, setMe] = useState<Me | null>(null);
  const [schoolId, setSchoolId] = useState("");
  const [curricula, setCurricula] = useState<Curriculum[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [curriculumId, setCurriculumId] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [lessonTitle, setLessonTitle] = useState("");
  const [lessonContent, setLessonContent] = useState("");
  const [duration, setDuration] = useState(40);
  const [preview, setPreview] = useState<Lesson | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const currentSchool = me?.schools.find((s) => s.school_id === schoolId);

  useEffect(() => {
    let active = true;
    api<Me>("/me")
      .then((data) => {
        if (!active) return;
        setMe(data);
        setSchoolId(data.schools[0]?.school_id || "");
        if (!data.schools.length) setError("Your administrator needs to add you to a school.");
      })
      .catch((e) => {
        if (active) setError(messageOf(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!schoolId) return;
    let active = true;
    Promise.all([api<Curriculum[]>("/curricula", schoolId), api<Lesson[]>("/lessons", schoolId)])
      .then(([c, l]) => {
        if (active) {
          setCurricula(c);
          setLessons(l);
        }
      })
      .catch((e) => {
        if (active) setError(messageOf(e));
      });
    return () => {
      active = false;
    };
  }, [schoolId]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [turns, busy]);

  function resetChat() {
    setTurns([]);
    setConversationId(undefined);
    setMessage("");
    setError("");
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || busy || !schoolId) return;
    const text = message.trim();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await api<ChatResponse>("/companion/chat", schoolId, {
        message: text,
        conversation_id: conversationId,
        curriculum_id: curriculumId || null,
      });
      setConversationId(result.conversation_id);
      setTurns((old) => [
        ...old,
        { role: "user", text },
        {
          role: "assistant",
          text: result.answer,
          sources: result.sources.map((s) => s.title),
        },
      ]);
      setMessage("");
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setBusy(false);
    }
  }

  async function saveLesson(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const record = await api<Lesson>("/lessons", schoolId, {
        title: lessonTitle,
        content: lessonContent,
        duration_minutes: duration,
        curriculum_id: curriculumId || null,
      });
      setLessons((old) => [record, ...old]);
      setLessonTitle("");
      setLessonContent("");
      setNotice("Lesson draft saved.");
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setBusy(false);
    }
  }

  async function addCurriculum(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form));
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const record = await api<Curriculum>("/curricula", schoolId, values);
      setCurricula((old) => [...old, record]);
      form.reset();
      setNotice("Curriculum added to your school.");
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setBusy(false);
    }
  }

  const titles = {
    companion: "A little support. More possibility.",
    curriculum: "Give every lesson a direction.",
    lessons: "Good lessons start with a plan.",
  };

  return (
    <div className="workspace">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <span className="brand-mark">
            d<span>e</span>
          </span>
          <span>
            debug ed<span className="brand-caption">A teacher’s workspace</span>
          </span>
        </Link>
        <div className="workspace-label">YOUR WORKSPACE</div>
        <nav aria-label="Workspace sections">
          {(["companion", "curriculum", "lessons"] as View[]).map((item, i) => (
            <button
              key={item}
              className={view === item ? "nav-item active" : "nav-item"}
              onClick={() => {
                setView(item);
                setError("");
                setNotice("");
              }}
            >
              <span aria-hidden="true" className="nav-symbol">
                {["✳", "▤", "▥"][i]}
              </span>
              {["AI companion", "Curriculum", "Lesson planner"][i]}
              <span className="nav-arrow">↗</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <span className="small-spark">✳</span>
          <p>
            More space for
            <br />
            the work that matters.
          </p>
          <span>Built around your teaching day.</span>
        </div>
        <div className="profile">
          <div className="avatar">
            {me?.name
              .split(" ")
              .map((n) => n[0])
              .slice(0, 2)
              .join("") || "TE"}
          </div>
          <div>
            <strong>{me?.name || "Teacher workspace"}</strong>
            <small>
              {currentSchool?.role === "admin" ? "School administrator" : "Teacher"}
              {isDemo ? " · Local demo" : ""}
            </small>
          </div>
        </div>
        {!isDemo && me && (
          <button className="logout" onClick={() => signOut().catch((e) => setError(messageOf(e)))}>
            Sign out
          </button>
        )}
      </aside>
      <main className="main">
        <header className="topbar">
          <span>
            Workspace <span className="crumb">/</span>{" "}
            <strong>
              {view === "companion"
                ? "AI companion"
                : view === "curriculum"
                  ? "Curriculum"
                  : "Lesson planner"}
            </strong>
          </span>
          {me && me.schools.length > 1 ? (
            <select
              aria-label="School"
              value={schoolId}
              disabled={busy}
              onChange={(e) => {
                setSchoolId(e.target.value);
                setCurricula([]);
                setLessons([]);
                setCurriculumId("");
                setLessonContent("");
                setLessonTitle("");
                setPreview(null);
                resetChat();
              }}
            >
              {me.schools.map((s) => (
                <option key={s.school_id} value={s.school_id}>
                  {s.school_name}
                </option>
              ))}
            </select>
          ) : (
            <span className="school-badge">
              <span className="status-dot" />
              {currentSchool?.school_name || "Your school"}
            </span>
          )}
        </header>
        <div className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">THOUGHTFUL TEACHING, TOGETHER</div>
              <h1>{titles[view]}</h1>
              <p>
                {view === "companion"
                  ? "Explore an idea, shape a lesson, or find a fresh way to explain it."
                  : view === "curriculum"
                    ? "Keep your school’s learning objectives close to your planning."
                    : "Turn your ideas into drafts you can bring to the classroom."}
              </p>
            </div>
            <span className="heading-art" aria-hidden="true">
              ✳
            </span>
          </div>
          {loading && <p role="status">Opening your workspace…</p>}
          {error && (
            <div className="alert error" role="alert">
              {error}
              {!isDemo && !me && (
                <button
                  className="button"
                  onClick={() => signIn().catch((e) => setError(messageOf(e)))}
                >
                  Sign in to your school
                </button>
              )}
            </div>
          )}
          {notice && (
            <div className="alert success" role="status">
              {notice}
            </div>
          )}
          {me && view === "companion" && (
            <div className="companion-layout">
              <section className="chat-panel" aria-label="Teaching companion">
                <div className="panel-header">
                  <span>
                    <span className="companion-icon">✳</span>
                    <strong>Your teaching companion</strong>
                  </span>
                  <button className="text-button" disabled={busy} onClick={resetChat}>
                    ＋ New chat
                  </button>
                </div>
                {me.ai_provider === "demo" && (
                  <div className="demo-banner">
                    Demo mode · Replies are fixed examples. No AI service is connected.
                  </div>
                )}
                <div className="chat-body" aria-live="polite">
                  {!turns.length && (
                    <div className="chat-welcome">
                      <div className="welcome-mark">✳</div>
                      <h2>What are we working on?</h2>
                      <p>
                        A starting point for your next great lesson.
                        <br />
                        You bring the expertise. Let’s make room for ideas.
                      </p>
                      <div className="suggestions">
                        {suggestions.map((s, i) => (
                          <button key={s} onClick={() => setMessage(s)}>
                            <span>0{i + 1}</span>
                            {s}
                            <b aria-hidden="true">↗</b>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {turns.map((turn, i) => (
                    <article key={i} className={`turn ${turn.role}`}>
                      <div className="turn-label">{turn.role === "user" ? "YOU" : "COMPANION"}</div>
                      <p>{turn.text}</p>
                      {!!turn.sources?.length && (
                        <small>Context supplied: {turn.sources.join(", ")}</small>
                      )}
                      {turn.role === "assistant" && (
                        <button
                          className="text-button"
                          onClick={() => {
                            setLessonContent(turn.text);
                            setLessonTitle("");
                            setView("lessons");
                            setNotice("Review the draft, add a title, and save when ready.");
                          }}
                        >
                          Use as a lesson draft ↗
                        </button>
                      )}
                    </article>
                  ))}
                  {busy && (
                    <p role="status" className="thinking">
                      Preparing your response…
                    </p>
                  )}
                  <div ref={bottom} />
                </div>
                <form onSubmit={send} className="composer">
                  <label className="sr-only" htmlFor="message">
                    Message your teaching companion
                  </label>
                  <textarea
                    id="message"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Help me plan a lesson about…"
                    rows={2}
                    maxLength={6000}
                    required
                    disabled={busy}
                  />
                  <div className="composer-bottom">
                    <span>Keep student names and private details out of chat.</span>
                    <button
                      className="send-button"
                      aria-label="Send message"
                      disabled={busy || !message.trim() || !schoolId}
                    >
                      ↑
                    </button>
                  </div>
                </form>
                <p className="review-note">
                  A helpful starting point. Always review AI suggestions before using them.
                </p>
              </section>
              <aside className="context-panel">
                <div className="eyebrow">MAKE IT RELEVANT</div>
                <h2>Your lesson context</h2>
                <p>Select a curriculum to give your companion the learning objectives.</p>
                <label htmlFor="curriculum-context">Curriculum</label>
                <select
                  id="curriculum-context"
                  value={curriculumId}
                  disabled={busy}
                  onChange={(e) => {
                    setCurriculumId(e.target.value);
                    resetChat();
                  }}
                >
                  <option value="">General teaching support</option>
                  {curricula.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.title}
                    </option>
                  ))}
                </select>
                {curriculumId ? (
                  curricula
                    .filter((c) => c.id === curriculumId)
                    .map((c) => (
                      <div className="context-record" key={c.id}>
                        <span className="pill">
                          {c.subject} · {c.grade}
                        </span>
                        <h3>{c.title}</h3>
                        <p>{c.objectives}</p>
                      </div>
                    ))
                ) : (
                  <div className="context-record">
                    <span className="pill">A fresh perspective</span>
                    <p>Without a selected curriculum, responses provide general guidance.</p>
                  </div>
                )}
                <div className="context-foot">
                  <span>✧</span> Your experience makes the difference. Adapt every idea to your
                  learners.
                </div>
              </aside>
            </div>
          )}
          {me && view === "curriculum" && (
            <div className="records-layout">
              <section>
                <h2 className="section-title">
                  School curriculum <span>{curricula.length}</span>
                </h2>
                <div className="record-list">
                  {curricula.map((c) => (
                    <article key={c.id} className="record">
                      <span className="pill">
                        {c.subject} · {c.grade}
                      </span>
                      <h2>{c.title}</h2>
                      <p>{c.objectives}</p>
                      <button
                        className="text-button"
                        onClick={() => {
                          setCurriculumId(c.id);
                          resetChat();
                          setView("companion");
                        }}
                      >
                        Plan with companion ↗
                      </button>
                    </article>
                  ))}
                  {!curricula.length && (
                    <div className="record">
                      <h2>A place for your learning objectives</h2>
                      <p>Your school’s curriculum records will appear here.</p>
                    </div>
                  )}
                </div>
              </section>
              {currentSchool?.role === "admin" && (
                <form className="form-panel" onSubmit={addCurriculum}>
                  <div className="eyebrow">SCHOOL LIBRARY</div>
                  <h2>Add curriculum</h2>
                  <label htmlFor="curriculum-title">Title</label>
                  <input
                    id="curriculum-title"
                    name="title"
                    required
                    maxLength={200}
                    placeholder="e.g. Living things & their habitats"
                  />
                  <div className="field-row">
                    <div>
                      <label htmlFor="subject">Subject</label>
                      <input id="subject" name="subject" required maxLength={100} />
                    </div>
                    <div>
                      <label htmlFor="grade">Year / grade</label>
                      <input id="grade" name="grade" required maxLength={50} />
                    </div>
                  </div>
                  <label htmlFor="objectives">Learning objectives</label>
                  <textarea id="objectives" name="objectives" required rows={7} maxLength={12000} />
                  <button className="button" disabled={busy}>
                    Add to curriculum
                  </button>
                </form>
              )}
            </div>
          )}
          {me && view === "lessons" && (
            <div className="records-layout">
              <section>
                <h2 className="section-title">
                  Your lesson drafts <span>{lessons.length}</span>
                </h2>
                <div className="record-list">
                  {lessons.map((l) => (
                    <article className="record" key={l.id}>
                      <span className="pill">Draft · {l.duration_minutes} minutes</span>
                      <h2>{l.title}</h2>
                      <p className="clamp">{l.content}</p>
                      <button className="text-button" onClick={() => setPreview(l)}>
                        Read lesson ↗
                      </button>
                    </article>
                  ))}
                  {!lessons.length && (
                    <div className="record">
                      <h2>Your next lesson starts here.</h2>
                      <p>Create a draft or bring an idea over from your companion.</p>
                    </div>
                  )}
                </div>
              </section>
              <form className="form-panel lesson-form" onSubmit={saveLesson}>
                <div className="eyebrow">ROOM FOR YOUR IDEAS</div>
                <h2>Create a lesson draft</h2>
                <label htmlFor="lesson-title">Lesson title</label>
                <input
                  id="lesson-title"
                  value={lessonTitle}
                  onChange={(e) => setLessonTitle(e.target.value)}
                  required
                  maxLength={200}
                />
                <label htmlFor="lesson-curriculum">Curriculum</label>
                <select
                  id="lesson-curriculum"
                  value={curriculumId}
                  onChange={(e) => {
                    setCurriculumId(e.target.value);
                    resetChat();
                  }}
                >
                  <option value="">No linked curriculum</option>
                  {curricula.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.title}
                    </option>
                  ))}
                </select>
                <label htmlFor="duration">Duration (minutes)</label>
                <input
                  id="duration"
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  min={5}
                  max={480}
                  required
                />
                <label htmlFor="lesson-content">Lesson plan</label>
                <textarea
                  id="lesson-content"
                  value={lessonContent}
                  onChange={(e) => setLessonContent(e.target.value)}
                  rows={10}
                  required
                  maxLength={20000}
                />
                <button className="button" disabled={busy}>
                  Save lesson draft
                </button>
              </form>
            </div>
          )}
          <footer>
            DEBUG ED <span>·</span> A foundation for better teaching days.
          </footer>
        </div>
      </main>
      {preview && (
        <dialog
          ref={(node) => {
            if (node && !node.open) node.showModal();
          }}
          onCancel={() => setPreview(null)}
          aria-label={preview.title}
          className="lesson-preview"
        >
          <button className="text-button" autoFocus onClick={() => setPreview(null)}>
            Close ×
          </button>
          <span className="pill">Draft · {preview.duration_minutes} minutes</span>
          <h2>{preview.title}</h2>
          <p>{preview.content}</p>
        </dialog>
      )}
    </div>
  );
}
