/**
 * AI-Based Drug Recommendation System
 * Client-Side Liquid Glass Interactions & Real-Time Symptom Filter
 */

document.addEventListener('DOMContentLoaded', () => {
  // CSRF token helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // 1. Searchable Symptom Filter
  const symptomSearchInput = document.getElementById('symptomSearchInput');
  const symptomTags = document.querySelectorAll('.symptom-tag-container');

  if (symptomSearchInput && symptomTags.length > 0) {
    symptomSearchInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
      symptomTags.forEach(el => {
        const name = el.getAttribute('data-name').toLowerCase();
        const display = el.getAttribute('data-display').toLowerCase();
        if (name.includes(term) || display.includes(term) || term === '') {
          el.style.display = 'inline-block';
        } else {
          el.style.display = 'none';
        }
      });
    });
  }

  // 2. Interactive Tag Selection (Sync with hidden checkbox)
  document.querySelectorAll('.symptom-tag').forEach(tag => {
    tag.addEventListener('click', () => {
      const checkboxId = tag.getAttribute('data-for');
      const checkbox = document.getElementById(checkboxId);
      if (checkbox) {
        checkbox.checked = !checkbox.checked;
        tag.classList.toggle('selected', checkbox.checked);
        updateEmergencyBanner();
      }
    });
  });

  // 3. Real-Time Emergency Banner Check
  function updateEmergencyBanner() {
    const emergencyBanner = document.getElementById('liveEmergencyBanner');
    if (!emergencyBanner) return;

    let hasEmergency = false;
    document.querySelectorAll('.symptom-tag.emergency.selected').forEach(() => {
      hasEmergency = true;
    });

    if (hasEmergency) {
      emergencyBanner.classList.remove('d-none');
    } else {
      emergencyBanner.classList.add('d-none');
    }
  }

  // 4. Natural Language Parsing Trigger Button
  const btnNlpParse = document.getElementById('btnNlpParse');
  const rawTextArea = document.getElementById('id_raw_symptom_text');

  if (btnNlpParse && rawTextArea) {
    btnNlpParse.addEventListener('click', async () => {
      const text = rawTextArea.value.trim();
      if (!text) {
        alert("Please type a symptom description to extract symptoms.");
        return;
      }

      btnNlpParse.disabled = true;
      btnNlpParse.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Analyzing text...';

      try {
        const res = await fetch(`/symptoms/api/nlp-extract/?text=${encodeURIComponent(text)}`);
        const data = await res.json();

        let addedCount = 0;
        data.matched_symptoms.forEach(sym => {
          const checkbox = document.querySelector(`input[name="selected_symptoms"][value="${sym.id}"]`);
          if (checkbox) {
            checkbox.checked = true;
            const tag = document.querySelector(`.symptom-tag[data-for="${checkbox.id}"]`);
            if (tag) tag.classList.add('selected');
            addedCount++;
          }
        });

        updateEmergencyBanner();

        const nlpFeedback = document.getElementById('nlpFeedback');
        if (nlpFeedback) {
          nlpFeedback.classList.remove('d-none');
          nlpFeedback.innerHTML = `<strong>NLP Extracted ${addedCount} symptom(s):</strong> ${data.matched_symptoms.map(s => s.display_name).join(', ') || 'No specific match found'}`;
        }
      } catch (err) {
        console.error("NLP error:", err);
      } finally {
        btnNlpParse.disabled = false;
        btnNlpParse.innerHTML = '<i class="bi bi-magic me-1"></i> Extract Symptoms from Text';
      }
    });
  }

  // 5. Dismiss Notification
  document.querySelectorAll('.btn-read-notification').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const notifId = btn.getAttribute('data-id');
      try {
        await fetch(`/dashboard/notification/${notifId}/read/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          }
        });
        const item = document.getElementById(`notif-item-${notifId}`);
        if (item) item.remove();
        const badge = document.getElementById('notificationCountBadge');
        if (badge) {
          let count = parseInt(badge.textContent) - 1;
          if (count <= 0) badge.style.display = 'none';
          else badge.textContent = count;
        }
      } catch (err) {
        console.error(err);
      }
    });
  });
});
