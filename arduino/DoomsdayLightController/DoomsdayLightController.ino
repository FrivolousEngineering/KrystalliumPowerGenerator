#include "FastLED.h"

constexpr uint32_t MaxCommandLength = 128;

DEFINE_GRADIENT_PALETTE(detected) {
    0,   0,   0,   0,
  108,  32,   0, 128,
  128,  64,  32, 128,
  148,  32,   0, 128,
  255,   0,   0,   0
};

DEFINE_GRADIENT_PALETTE(activate) {
    0,   0,   0,   0,
  128,  64,  32, 128,
  255,  32,   0, 128
};

DEFINE_GRADIENT_PALETTE(active) {
    0,  32, 0, 128,
  128,   0, 0, 128,
  255,  32, 0, 128
};

DEFINE_GRADIENT_PALETTE(fade_out) {
    0, 32, 0, 128,
  128,  0, 0,  32,
  250,  0, 0,   0,
  255,  0, 0,   0
};

DEFINE_GRADIENT_PALETTE(overload) {
    0,  32,   0, 128,
  128, 128,  32, 128,
  255, 255, 255, 255
};

enum class State {
  Inactive,
  Active,
  Fadeout,
  Overload,
};

State currentState;

template <uint8_t Pin, int LedCount>
struct Side {
  Side() {
    fill_solid(leds, LedCount, CRGB::Black);
    controller = &FastLED.addLeds<NEOPIXEL, Pin>(leds, LedCount);
    controller->showLeds(255);
  }

  void set_color(CRGB color) {
    fill_solid(leds, LedCount, color);
    controller->showLeds(255);
  }

  void animate(CRGBPalette16 _palette, uint8_t from, uint8_t to, float duration, float variation = 0.1)
  {
    palette = _palette;
    current = from;
    target = to;

    auto steps = duration * 1000 / update_rate;
    speed = (target - current) / steps;
    
    if (target > current) {
      speed = speed;
    } else if (target < current) {
      speed = -speed;
    }
  }

  void update(int millis) {
    // Rate limit to a certain amount of millis per update
    if ((millis - lastUpdate) < update_rate) {
      return;
    }

    if (target == current) {
      return;
    }

    current += speed;
    if (abs(current) >= target) {
      current = target;
    }

    for (int i = 0; i < LedCount; ++i) {
      int16_t value = uint8_t(current) + (random(10) - 5);
      auto intensity = 128 + random(127);
      auto color = ColorFromPalette(palette, constrain(value, 0, 255), intensity);
      leds[i] = color;
    }

    controller->showLeds(255);

    lastUpdate = millis;
  }

  CRGB leds[LedCount];
  CRGBPalette16 palette;
  CLEDController* controller = nullptr;
  
  float current = 0.0f;
  float target = 0.0f;
  float speed = 0.0f;

  int update_rate = 2;
  int lastUpdate = 0;
};

Side<D1, 45> left;
Side<D2, 24> right;

void setup() {
  randomSeed(analogRead(A0));

  left.set_color(CRGB::Black);
  right.set_color(CRGB::Black);

  Serial.begin(115200);
  Serial.println("Booted");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  int now = millis();
  left.update(now);
  right.update(now);

  if (currentState == State::Active) {
    if (left.current >= left.target) {
      left.animate(active, 0, 255, 30);
    }
    if (right.current >= right.target) {
      right.animate(active, 0, 255, 30);
    }
  }
}

void trim(char* str) {
  int len = strlen(str);
  while (len > 0 && (str[len - 1] == '\r' || str[len - 1] == '\n' || str[len - 1] == ' ')) {
    str[--len] = '\0';
  }
}

void processCommand(String command) {

  char cmdBuffer[MaxCommandLength];
  memset(cmdBuffer, 0, sizeof(cmdBuffer));  // Clear buffer to prevent leftover data

  // Ensure we don't overflow
  int len = command.length();
  if (len >= MaxCommandLength) {
    Serial.println("Command too long");
    return;
  }
  command.toCharArray(cmdBuffer, MaxCommandLength);
  cmdBuffer[sizeof(cmdBuffer) - 1] = '\0';
  
  trim(cmdBuffer);  // Trim newlines and trailing spaces

  char* keyword = strtok(cmdBuffer, " ");
  char* argument = strtok(NULL, "");

  if (keyword == NULL) return;
  strupr(keyword);  // Convert keyword to uppercase

  if (argument != NULL && strcmp(keyword, "WRITE") != 0) {
    strupr(argument);
  }
  
  if (strcmp(keyword, "NAME") == 0) {
    handleNameCommand(argument);
  } else if (strcmp(keyword, "DETECTED") == 0) {
    handleDetectedCommand(argument);
  } else if (strcmp(keyword, "SETSTATE") == 0) {
    handleSetStateCommand(argument);
  }
  
  
  /*else if (strcmp(keyword, "ACTIVATE") == 0) {
    handleActivateCommand(argument);
  } else if (strcmp(keyword, "FADEOUT") == 0) {
    handleFadeOutCommand(argument);
  } else if (strcmp(keyword, "OVERLOAD") == 0) {
    handleOverloadCommand(argument);
  }*/
}

void handleNameCommand(char* argument) {
  if (argument != NULL) {
    Serial.println("Setting the name is not supported!");
  } 
  else {
    Serial.println("Name: DOOMSDAY");
  }
}

void handleDetectedCommand(char* arguments) {
  char* side = strtok(arguments, " ");

  if (side == NULL) {
    Serial.println("DETECTED requires argument LEFT or RIGHT");
    return;
  }

  if (currentState != State::Inactive) {
    return;
  }

  if (strcmp(side, "LEFT") == 0) {
    left.animate(detected, 0, 255, 1);
  } else {
    right.animate(detected, 0, 255, 1);
  }
}

void handleSetStateCommand(char* arguments)
{
  char* state = strtok(arguments, " ");

  if (state == NULL) {
    Serial.println("SETSTATE requires argument STATE");
    return;
  }

  State newState;

  if (strcmp(state, "ACTIVE") == 0) {
    newState = State::Active;
  } else if (strcmp(state, "INACTIVE") == 0) {
    newState = State::Inactive;
  } else if (strcmp(state, "FADEOUT") == 0) {
    newState = State::Fadeout;
  } else if (strcmp(state, "OVERLOAD") == 0) {
    newState = State::Overload;
  }

  if (newState == currentState) {
    return;
  }

  switch (newState) {
    case State::Inactive:
      left.animate(activate, 255, 0, 2);
      right.animate(activate, 255, 0, 2);
      break;
    case State::Active:
      left.animate(activate, 0, 255, 2);
      right.animate(activate, 0, 255, 2);
      break;
    case State::Fadeout:
      left.animate(fade_out, 0, 255, 10);
      right.animate(fade_out, 0, 255, 10);
      break;
    case State::Overload:
      left.animate(overload, 0, 255, 10);
      right.animate(overload, 0, 255, 10);
      break;
  }

  currentState = newState;
}
/*
void handleActivateCommand(char* arguments)
{
  left.animate(activate, 0, 255, 2);
  right.animate(activate, 0, 255, 2);
}

void handleFadeOutCommand(char* arguments)
{
  left.animate(fade_out, 0, 255, 10);
  right.animate(fade_out, 0, 255, 10);
}

void handleOverloadCommand(char* arguments)
{
  left.animate(overload, 0, 255, 10);
  right.animate(overload, 0, 255, 10);
}*/
