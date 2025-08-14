package main

import (
	"encoding/json"
	"time"
)

// Parse an RFC3339 string as time if look like time.Time
func tryParseTime(s string) (time.Time, bool) {

	var t time.Time
	var err error

	t, err = time.Parse(time.RFC3339Nano, s)

	if err == nil {
		return t, true
	}

	t, err = time.Parse("2006-01-02", s)
	if err == nil {
		return t, true
	}

	return time.Time{}, false

}

// catch args
func jsonToArgs(raw []byte) ([]any, error) {

	if len(raw) == 0 {
		return nil, nil
	}

	var arr []any

	err := json.Unmarshal(raw, &arr)
	if err != nil {
		return nil, err
	}

	out := make([]any, 0, len(arr))

	for _, v := range arr {

		switch value := v.(type) {
		case nil:
			out = append(out, nil)
		case bool:
			out = append(out, value)
		case float64:
			// se for inteiro exato, converte p/ int64
			if value == float64(int64(value)) {
				out = append(out, int64(value))
			} else {
				out = append(out, value)
			}
		case string:
			// é datetime?
			t, ok := tryParseTime(value)
			if ok {
				out = append(out, t)
			} else {
				out = append(out, value)
			}
		default:
			// onj/arrays: JSON string
			b, _ := json.Marshal(value)
			out = append(out, b)
		}

	}

	return out, nil

}
