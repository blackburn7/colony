import { Component } from '@angular/core'

@Component({
	selector: 'header',
	standalone: true,
	template: `
		<div>
			<p>colony</p>
		</div>
	`,
	styles: `
		p {
			margin: 2rem;
			text-align: center;
		}
	`
})
export class Header {
	title = 'header'
}
