package main

import (
	"encoding/json"
	"io"
	"os"
	"stravago/stravago"
)

type Config struct {
	ClientID     string `json:"client_id"`
	ClientSecret string `json:"client_secret"`
	RefreshToken string `json:"refresh_token"`
}

func writeToFile(path string, data []byte) {
	f, err := os.Create(path)
	if err != nil {
		panic(err)
	}
	f.Write(data)
	f.Close()
}

func main() {
	f, err := os.Open("../../user/bram.json")
	if err != nil {
		panic(err)
	}
	// Read the contents of the file
	data, err := io.ReadAll(f)
	if err != nil {
		panic(err)
	}

	// parse json into config struct
	var config Config
	err = json.Unmarshal(data, &config)
	if err != nil {
		panic(err)
	}

	new_refresh_token := stravago.Authenticate(config.ClientID, config.ClientSecret, config.RefreshToken)
	config.RefreshToken = new_refresh_token
	configJSON, err := json.Marshal(config)
	if err != nil {
		panic(err)
	}

	f.Write(configJSON)
	f.Close()

	volume_result := stravago.GetWeeklyVolumes()
	if volume_result == "" {
		panic("volume_result is empty")
	}
	writeToFile("../../data/weekly_volumes.json", []byte(volume_result))

	pace_hr_result := stravago.GetPaceAndHeartRate()
	if len(pace_hr_result) < 50 {
		panic("received empty pace_hr data")
	}
	writeToFile("../../data/pace_hr.json", []byte(pace_hr_result))

	totals := stravago.GetAthleteRunningStats()
	if len(totals) < 50 {
		panic("received empty running totals")
	}
	writeToFile("../../data/running_total.json", totals)

	map_lines := stravago.GetActivitiesOnMap()
	if len(map_lines) < 50 {
		panic("receied empty running map")
	}
	writeToFile("../../data/running_map.json", []byte(map_lines))
}
